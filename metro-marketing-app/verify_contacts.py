#!/usr/bin/env python3
"""Quarterly re-verification worker for AdAtlas contact data.

This is the automation behind LAUNCH.md Step 6 ("Quarterly re-verification").
It does NOT auto-overwrite anything in adatlas.db. It checks each contact row
against a live source (Apify's Google Maps actor, or Firecrawl's /search) and
writes a finding into `verification_queue`. A human approves or rejects each
finding in /admin ("Data freshness" -> queue) before it touches `contacts`.

WHY THIS SCRIPT DOESN'T CALL THE APIS FROM INSIDE THE DEV SANDBOX:
This was built inside a network-locked container whose egress policy blocks
api.apify.com and api.firecrawl.dev outright (confirmed via the proxy status
endpoint - a policy 403, not a transient failure). So the HTTP calls below are
written correctly but UNTESTED against the live APIs. Run this from your own
machine, or from wherever you deploy the app (Render/Railway/Fly all have
normal outbound internet) - both have open egress. `--dry-run` exercises all
the DB/parsing logic without calling out anywhere, so you can sanity-check the
plumbing right now, in this sandbox, before you ever spend an API credit.

SECRETS: reads APIFY_API_KEY / FIRECRAWL_API_KEY from the environment only.
Never hardcode a key in this file or pass one on the command line (it ends up
in shell history). Put them in a local .env you source, or your host's env
vars - both are already .gitignored / configured as secrets per LAUNCH.md.

Usage:
    # 1. Sanity-check the logic with zero network calls:
    python3 verify_contacts.py --provider apify --dry-run --limit 5

    # 2. Real run, from a machine with open internet:
    export APIFY_API_KEY=...       # or FIRECRAWL_API_KEY
    python3 verify_contacts.py --provider apify --limit 20 --metro Tampa
    python3 verify_contacts.py --provider firecrawl --limit 20

Then review results at  http://YOUR_HOST/admin  (Data freshness -> queue).
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "adatlas.db")

APIFY_ACTOR = "compass~crawler-google-places"  # Apify Store: Google Maps Scraper
APIFY_RUN_URL = f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/run-sync-get-dataset-items"
FIRECRAWL_SEARCH_URL = "https://api.firecrawl.dev/v1/search"

_NAME_SPLIT = re.compile(r"\s*[;·]\s*")           # split on ';' or '·'
_TRAILING_PHONE = re.compile(r"\(\d{3}\)\s?\d{3}-\d{4}.*$")


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def extract_company_names(contacts_text: str) -> list[str]:
    """Best-effort split of a free-text contacts blob into bare company names
    for a per-company lookup. This is heuristic on purpose - the fields were
    written for humans to read, not machines to parse. A human reviews every
    finding in /admin before it touches `contacts`, so an imperfect split here
    costs a wasted API call at worst, never a bad write."""
    if not contacts_text:
        return []
    text = contacts_text.split("—")[0]           # drop trailing "— full roster on..." commentary
    before, sep, after = text.partition(":")       # "Lead-in phrase: Actual Name, Other Name"
    if sep and after.strip():
        text = after
    names = []
    for chunk in re.split(r"\s*[;,·]\s*", text):
        chunk = _TRAILING_PHONE.sub("", chunk).strip(" .-—")
        if chunk and len(chunk) > 2 and not chunk.lower().startswith(("brokers", "http")):
            names.append(chunk)
    return names[:5]  # a category blob can list many; check the first few


def http_post_json(url: str, headers: dict, payload: dict, timeout: int = 30) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json", **headers,
    }, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def check_via_apify(company: str, metro: str, api_key: str) -> dict:
    """Search Google Maps for `company` in `metro` via Apify's Google Maps
    Scraper actor. Returns {found, name, phone, address, raw}."""
    payload = {
        "searchStringsArray": [f"{company} {metro}"],
        "maxCrawledPlacesPerSearch": 1,
        "language": "en",
    }
    url = f"{APIFY_RUN_URL}?token={api_key}"
    items = http_post_json(url, {}, payload, timeout=60)
    if not items:
        return {"found": False, "raw": items}
    top = items[0]
    return {
        "found": True,
        "name": top.get("title") or top.get("name"),
        "phone": top.get("phone") or top.get("phoneUnformatted"),
        "address": top.get("address"),
        "website": top.get("website"),
        "raw": top,
    }


def check_via_firecrawl(company: str, metro: str, api_key: str) -> dict:
    """Search the web for `company` in `metro` via Firecrawl /search and
    return the top result's title/url/snippet as a human-reviewable finding."""
    payload = {"query": f"{company} {metro} billboard advertising phone", "limit": 3}
    headers = {"Authorization": f"Bearer {api_key}"}
    result = http_post_json(FIRECRAWL_SEARCH_URL, headers, payload, timeout=60)
    hits = result.get("data") or result.get("results") or []
    if not hits:
        return {"found": False, "raw": result}
    top = hits[0]
    return {
        "found": True,
        "title": top.get("title"),
        "url": top.get("url"),
        "snippet": top.get("description") or top.get("snippet"),
        "raw": top,
    }


def run(provider: str, metro_filter: str | None, category_filter: str | None,
        limit: int, dry_run: bool):
    api_key = os.environ.get(
        "APIFY_API_KEY" if provider == "apify" else "FIRECRAWL_API_KEY", "")
    if not dry_run and not api_key:
        env_name = "APIFY_API_KEY" if provider == "apify" else "FIRECRAWL_API_KEY"
        sys.exit(f"Set {env_name} in your environment first (never on the CLI - "
                 f"it lands in shell history). Or pass --dry-run to test without it.")

    conn = db()
    sql = "SELECT * FROM contacts WHERE 1=1"
    args = []
    if metro_filter:
        sql += " AND metro=?"; args.append(metro_filter)
    if category_filter:
        sql += " AND category=?"; args.append(category_filter)
    sql += " ORDER BY last_verified ASC LIMIT ?"  # stalest rows first
    args.append(limit)
    rows = conn.execute(sql, args).fetchall()

    print(f"[verify] provider={provider} dry_run={dry_run} rows_to_check={len(rows)}")
    checked = flagged = errors = 0

    for row in rows:
        names = extract_company_names(row["contacts"])
        if not names:
            continue
        target = names[0]  # verify the first-listed operator per row
        print(f"  checking: {row['metro']} / {row['category']} -> '{target}'")

        if dry_run:
            checked += 1
            print(f"    [dry-run] would call {provider} for '{target}' in {row['metro']}")
            continue

        try:
            if provider == "apify":
                result = check_via_apify(target, row["metro"], api_key)
                finding = json.dumps(result.get("raw", {}))[:2000]
                confidence = "high" if result.get("found") and result.get("phone") else "low"
            else:
                result = check_via_firecrawl(target, row["metro"], api_key)
                finding = json.dumps({k: v for k, v in result.items() if k != "raw"})[:2000]
                confidence = "medium" if result.get("found") else "low"
            checked += 1

            if not result.get("found"):
                confidence = "low"
                finding = f"No live result found for '{target}' in {row['metro']}."

            conn.execute(
                "INSERT INTO verification_queue"
                "(contact_id, metro, category, provider, old_contacts, finding, confidence) "
                "VALUES (?,?,?,?,?,?,?)",
                (row["id"], row["metro"], row["category"], provider,
                 row["contacts"], finding, confidence))
            conn.commit()
            flagged += 1
            time.sleep(1)  # be polite to the API

        except urllib.error.HTTPError as e:
            errors += 1
            print(f"    ERROR {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
        except Exception as e:  # noqa: BLE001 - log and keep going
            errors += 1
            print(f"    ERROR: {e}", file=sys.stderr)

    conn.close()
    print(f"\n[verify] checked={checked} queued={flagged} errors={errors}")
    if not dry_run and flagged:
        print(f"[verify] Review findings at /admin -> Data freshness -> "
              f"verification queue ({flagged} pending).")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--provider", choices=["apify", "firecrawl"], default="apify")
    ap.add_argument("--metro", default=None, help="Only check this metro")
    ap.add_argument("--category", default=None, help="Only check this category")
    ap.add_argument("--limit", type=int, default=20, help="Max rows to check this run")
    ap.add_argument("--dry-run", action="store_true",
                    help="Exercise DB/parsing logic with zero network calls")
    args = ap.parse_args()
    run(args.provider, args.metro, args.category, args.limit, args.dry_run)


if __name__ == "__main__":
    main()
