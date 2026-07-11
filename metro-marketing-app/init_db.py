#!/usr/bin/env python3
"""Build adatlas.db (SQLite) from data.json.

Adds the production fields the static prototype lacked:
  * last_verified / verified_by on every contact + metro row (the trust signal)
  * users / sessions (auth), claims (vendor claim flow)
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "adatlas.db")
DATA_VERIFIED = "2026-07-08"          # when the dataset was compiled/verified
VERIFIED_BY = "adatlas-research"


def main():
    with open(os.path.join(HERE, "data.json")) as fh:
        data = json.load(fh)

    if os.path.exists(DB):
        os.remove(DB)
    db = sqlite3.connect(DB)
    c = db.cursor()
    c.executescript("""
    CREATE TABLE metros(
      rank INTEGER, metro TEXT PRIMARY KEY, state TEXT, dma TEXT, pop TEXT,
      ooh_rate TEXT, ooh_ops INTEGER, paper TEXT, bizj TEXT, tv TEXT,
      radio TEXT, spanish TEXT, agencies TEXT, note TEXT,
      last_verified TEXT, verified_by TEXT);
    CREATE TABLE contacts(
      id INTEGER PRIMARY KEY AUTOINCREMENT, metro TEXT, category TEXT,
      scope TEXT, contacts TEXT, last_verified TEXT, verified_by TEXT);
    CREATE TABLE tactics(
      id INTEGER PRIMARY KEY AUTOINCREMENT, cat TEXT, tactic TEXT, cost TEXT,
      rel TEXT, ih TEXT, time TEXT, note TEXT);
    CREATE TABLE budgets(channel TEXT, b25 INTEGER, b50 INTEGER, b100 INTEGER, why TEXT);
    CREATE TABLE calendar(month TEXT, context TEXT, push TEXT, channels TEXT);
    CREATE TABLE users(
      id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, pw_hash TEXT,
      salt TEXT, plan TEXT DEFAULT 'free', created TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE sessions(
      token TEXT PRIMARY KEY, user_id INTEGER, created TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE claims(
      id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT, metro TEXT,
      email TEXT, message TEXT, status TEXT DEFAULT 'pending',
      created TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE INDEX idx_contacts_metro ON contacts(metro);
    CREATE INDEX idx_tactics_cat ON tactics(cat);
    """)

    for m in data["metros"]:
        c.execute("INSERT INTO metros VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (m["rank"], m["metro"], m["state"], str(m["dma"]), m["pop"],
                   m["oohRate"], m["oohOps"], m["paper"], m["bizj"], m["tv"],
                   m["radio"], m["spanish"], m["agencies"], m["note"],
                   DATA_VERIFIED, VERIFIED_BY))
    for r in data["contacts"]:
        c.execute("INSERT INTO contacts(metro,category,scope,contacts,last_verified,verified_by) "
                  "VALUES(?,?,?,?,?,?)",
                  (r["metro"], r["category"], r["scope"], r["contacts"],
                   DATA_VERIFIED, VERIFIED_BY))
    for t in data["tactics"]:
        c.execute("INSERT INTO tactics(cat,tactic,cost,rel,ih,time,note) VALUES(?,?,?,?,?,?,?)",
                  (t["cat"], t["t"], t["cost"], t["rel"], t["ih"], t["time"], t["note"]))
    for b in data["budgets"]:
        c.execute("INSERT INTO budgets VALUES(?,?,?,?,?)",
                  (b["channel"], b["b25"], b["b50"], b["b100"], b["why"]))
    for r in data["calendar"]:
        c.execute("INSERT INTO calendar VALUES(?,?,?,?)",
                  (r["month"], r["context"], r["push"], r["channels"]))
    db.commit()
    for table in ("metros", "contacts", "tactics"):
        n = c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {n}")
    db.close()
    print(f"adatlas.db written")


if __name__ == "__main__":
    main()
