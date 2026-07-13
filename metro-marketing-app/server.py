#!/usr/bin/env python3
"""AdAtlas API server (FastAPI + SQLite).

Production-shaped backend for the prototype:
  * auth: signup / login / logout with PBKDF2 password hashing + session tokens
  * subscription: plan lives on the user record, enforced SERVER-SIDE
      - free  -> 5 unlocked categories per market, 25 tactics per query, 10 quick wins
      - pro   -> everything
    /api/subscribe uses Stripe Checkout when STRIPE_SECRET_KEY is set,
    otherwise runs in mock mode (flips the plan directly) for local demo.
  * data: served from adatlas.db with last_verified on every contact row
  * vendor side: POST /api/claim files a listing claim (pending review)

Run:  python3 server.py            (http://localhost:8000)
"""
from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "adatlas.db")
STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")          # Pro $49/mo price
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "dev-admin")  # set a real one in prod
SMTP_HOST = os.environ.get("SMTP_HOST", "")               # email provider (optional)
FREE_CATS = {"Outdoor / OOH", "Print", "Digital - Search & Display",
             "Local & Direct", "Partnership & Channel"}
FREE_TACTIC_CAP = 25
FREE_WINS_CAP = 10

app = FastAPI(title="AdAtlas API")


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def migrate():
    """Additive tables introduced after init_db.py - safe on an existing DB."""
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS password_resets(
      token TEXT PRIMARY KEY, user_id INTEGER, expires TEXT);
    CREATE TABLE IF NOT EXISTS verified_listings(
      id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT, metro TEXT,
      claimed_by TEXT, verified_on TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(company, metro));
    CREATE TABLE IF NOT EXISTS leads(
      id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, metro TEXT,
      budget TEXT, business TEXT, source TEXT,
      created TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS verification_queue(
      id INTEGER PRIMARY KEY AUTOINCREMENT, contact_id INTEGER,
      metro TEXT, category TEXT, provider TEXT,
      old_contacts TEXT, finding TEXT, confidence TEXT,
      status TEXT DEFAULT 'pending',
      created TEXT DEFAULT CURRENT_TIMESTAMP,
      reviewed TEXT);
    """)
    try:  # attribution on signups (additive column; ignore if it exists)
        conn.execute("ALTER TABLE users ADD COLUMN source TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    conn.commit(); conn.close()


migrate()


# ---------------------------------------------------------------- auth utils
def hash_pw(pw: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 200_000).hex()


def current_user(request: Request):
    token = request.cookies.get("ms_session")
    if not token:
        return None
    conn = db()
    row = conn.execute(
        "SELECT u.* FROM users u JOIN sessions s ON s.user_id=u.id WHERE s.token=?",
        (token,)).fetchone()
    conn.close()
    return row


class Credentials(BaseModel):
    email: str
    password: str
    source: str = ""       # utm/referrer attribution, set by the frontend


class Lead(BaseModel):
    email: str
    metro: str = ""
    budget: str = ""
    business: str = ""
    source: str = ""


class Claim(BaseModel):
    company: str
    metro: str
    email: str
    message: str = ""


@app.post("/api/signup")
def signup(creds: Credentials, response: Response):
    email = creds.email.strip().lower()
    if "@" not in email or len(creds.password) < 8:
        raise HTTPException(400, "Valid email and a password of 8+ characters required.")
    conn = db()
    if conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
        conn.close()
        raise HTTPException(409, "That email already has an account - log in instead.")
    salt = secrets.token_hex(16)
    cur = conn.execute("INSERT INTO users(email,pw_hash,salt,source) VALUES(?,?,?,?)",
                       (email, hash_pw(creds.password, salt), salt,
                        (creds.source or "")[:200]))
    token = secrets.token_urlsafe(32)
    conn.execute("INSERT INTO sessions(token,user_id) VALUES(?,?)", (token, cur.lastrowid))
    conn.commit(); conn.close()
    response.set_cookie("ms_session", token, httponly=True, samesite="lax")
    return {"email": email, "plan": "free"}


@app.post("/api/login")
def login(creds: Credentials, response: Response):
    email = creds.email.strip().lower()
    conn = db()
    row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not row or hash_pw(creds.password, row["salt"]) != row["pw_hash"]:
        conn.close()
        raise HTTPException(401, "Email or password doesn't match.")
    token = secrets.token_urlsafe(32)
    conn.execute("INSERT INTO sessions(token,user_id) VALUES(?,?)", (token, row["id"]))
    conn.commit(); conn.close()
    response.set_cookie("ms_session", token, httponly=True, samesite="lax")
    return {"email": row["email"], "plan": row["plan"]}


@app.post("/api/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get("ms_session")
    if token:
        conn = db()
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))
        conn.commit(); conn.close()
    response.delete_cookie("ms_session")
    return {"ok": True}


@app.get("/api/me")
def me(request: Request):
    u = current_user(request)
    if not u:
        return {"email": None, "plan": "free"}
    return {"email": u["email"], "plan": u["plan"]}


# ------------------------------------------------------------- subscription
@app.post("/api/subscribe")
def subscribe(request: Request):
    u = current_user(request)
    if not u:
        raise HTTPException(401, "Create an account first, then upgrade.")
    if STRIPE_KEY and PRICE_ID:
        import stripe  # only needed when actually configured
        stripe.api_key = STRIPE_KEY
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": PRICE_ID, "quantity": 1}],
            success_url=str(request.base_url) + "?upgraded=1",
            cancel_url=str(request.base_url),
            customer_email=u["email"],
            metadata={"user_id": u["id"]},
        )
        return {"checkout_url": session.url}
    # Mock mode: no Stripe configured - flip the plan directly for the demo.
    conn = db()
    conn.execute("UPDATE users SET plan='pro' WHERE id=?", (u["id"],))
    conn.commit(); conn.close()
    return {"plan": "pro", "mock": True}


@app.post("/api/stripe-webhook")
async def stripe_webhook(request: Request):
    """Stripe calls this on checkout completion; flips the plan.
    Signature verification requires STRIPE_WEBHOOK_SECRET in production."""
    payload = await request.json()
    if payload.get("type") == "checkout.session.completed":
        uid = payload["data"]["object"].get("metadata", {}).get("user_id")
        if uid:
            conn = db()
            conn.execute("UPDATE users SET plan='pro' WHERE id=?", (uid,))
            conn.commit(); conn.close()
    return {"received": True}


# --------------------------------------------------------------------- data
@app.get("/api/metros")
def metros():
    conn = db()
    rows = [dict(r) for r in conn.execute("SELECT * FROM metros ORDER BY rank")]
    conn.close()
    return rows


@app.get("/api/contacts")
def contacts(request: Request, metro: str):
    u = current_user(request)
    pro = bool(u and u["plan"] == "pro")
    conn = db()
    rows = conn.execute("SELECT * FROM contacts WHERE metro=?", (metro,)).fetchall()
    conn.close()
    out = []
    for r in rows:
        locked = (not pro) and r["category"] not in FREE_CATS
        out.append({
            "category": r["category"], "scope": r["scope"],
            "contacts": None if locked else r["contacts"],
            "locked": locked, "last_verified": r["last_verified"],
        })
    return {"metro": metro, "plan": "pro" if pro else "free", "categories": out}


@app.get("/api/tactics")
def tactics(request: Request, q: str = "", cat: str = "", cost: str = "",
            rel: str = "", time: str = ""):
    u = current_user(request)
    pro = bool(u and u["plan"] == "pro")
    sql = "SELECT cat,tactic,cost,rel,ih,time,note FROM tactics WHERE 1=1"
    args = []
    if q:
        sql += " AND (tactic LIKE ? OR note LIKE ?)"; args += [f"%{q}%", f"%{q}%"]
    for col, val in (("cat", cat), ("cost", cost), ("rel", rel), ("time", time)):
        if val:
            sql += f" AND {col}=?"; args.append(val)
    conn = db()
    rows = [dict(r) for r in conn.execute(sql, args)]
    conn.close()
    total = len(rows)
    capped = (not pro) and total > FREE_TACTIC_CAP
    if capped:
        rows = rows[:FREE_TACTIC_CAP]
    return {"total": total, "capped": capped, "rows": rows}


@app.get("/api/quickwins")
def quickwins(request: Request):
    u = current_user(request)
    pro = bool(u and u["plan"] == "pro")
    conn = db()
    rows = [dict(r) for r in conn.execute(
        "SELECT cat,tactic,time,note FROM tactics "
        "WHERE rel='High' AND cost='$' AND ih='Yes'")]
    conn.close()
    total = len(rows)
    capped = (not pro) and total > FREE_WINS_CAP
    if capped:
        rows = rows[:FREE_WINS_CAP]
    return {"total": total, "capped": capped, "rows": rows}


@app.get("/api/playbook")
def playbook(request: Request):
    u = current_user(request)
    if not (u and u["plan"] == "pro"):
        raise HTTPException(402, "Playbook tools are a Pro feature.")
    conn = db()
    budgets = [dict(r) for r in conn.execute("SELECT * FROM budgets")]
    calendar = [dict(r) for r in conn.execute("SELECT * FROM calendar")]
    conn.close()
    return {"budgets": budgets, "calendar": calendar}


# ------------------------------------------------- lead magnet: free plan
BUDGET_COL = {"2500": "b25", "5000": "b50", "10000": "b100"}


@app.get("/api/plan")
def plan(metro: str, budget: str = "2500"):
    """Public, ungated: a personalized starter plan for metro + budget.
    Deliberately generous - this is the lead magnet that converts SEO traffic."""
    col = BUDGET_COL.get(budget, "b25")
    conn = db()
    m = conn.execute("SELECT * FROM metros WHERE metro=?", (metro,)).fetchone()
    if not m:
        conn.close()
        raise HTTPException(404, "Unknown metro.")
    budgets = [{"channel": r["channel"], "amount": r[col], "why": r["why"]}
               for r in conn.execute("SELECT * FROM budgets")
               if r[col] and r[col] > 0]
    wins = [dict(r) for r in conn.execute(
        "SELECT cat,tactic,time,note FROM tactics "
        "WHERE rel='High' AND cost='$' AND ih='Yes' AND time='Fast' LIMIT 8")]
    free_contacts = [dict(r) for r in conn.execute(
        "SELECT category,scope,contacts FROM contacts WHERE metro=? AND category IN "
        "('Outdoor / OOH','Print','Local & Direct')", (metro,))]
    conn.close()
    return {
        "metro": m["metro"], "state": m["state"], "pop": m["pop"],
        "dma": m["dma"], "ooh_rate": m["ooh_rate"], "paper": m["paper"],
        "budget_monthly": int(budget), "allocation": budgets,
        "first_moves": wins, "local_contacts": free_contacts,
    }


@app.post("/api/lead")
def capture_lead(body: Lead):
    if "@" not in body.email:
        raise HTTPException(400, "A valid email is required.")
    conn = db()
    conn.execute("INSERT INTO leads(email,metro,budget,business,source) VALUES(?,?,?,?,?)",
                 (body.email.strip().lower(), body.metro, body.budget,
                  body.business[:120], (body.source or "")[:200]))
    conn.commit(); conn.close()
    # In production this also enrolls the address in the welcome sequence
    # (emails/ folder) via your ESP. Dev mode just logs it.
    print(f"[lead] {body.email} metro={body.metro} budget={body.budget} src={body.source}")
    return {"ok": True, "note": "Plan saved - check your inbox. (Demo: email delivery "
                                "activates once SMTP/ESP is configured.)"}


@app.get("/plan")
def plan_page():
    return FileResponse(os.path.join(HERE, "web", "plan.html"))


# ------------------------------------------------------------ password reset
class ResetRequest(BaseModel):
    email: str


class ResetComplete(BaseModel):
    token: str
    password: str


def send_reset_email(email: str, token: str):
    """Pluggable delivery. With SMTP_HOST configured, send real mail; in dev,
    print to the server log."""
    if SMTP_HOST:
        # import smtplib; build MIME + send. Left to deployment config.
        pass
    print(f"[reset-email] to={email} token={token}")


@app.post("/api/request-reset")
def request_reset(body: ResetRequest):
    import datetime
    email = body.email.strip().lower()
    conn = db()
    row = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
    resp = {"ok": True,
            "note": "If that email has an account, a reset link is on its way."}
    if row:
        token = secrets.token_urlsafe(24)
        expires = (datetime.datetime.utcnow()
                   + datetime.timedelta(hours=2)).isoformat()
        conn.execute("INSERT INTO password_resets VALUES(?,?,?)",
                     (token, row["id"], expires))
        conn.commit()
        send_reset_email(email, token)
        if not SMTP_HOST:      # dev/demo only: surface the token in the response
            resp["dev_token"] = token
    conn.close()
    return resp


@app.post("/api/reset")
def reset(body: ResetComplete):
    import datetime
    if len(body.password) < 8:
        raise HTTPException(400, "Password must be 8+ characters.")
    conn = db()
    row = conn.execute("SELECT * FROM password_resets WHERE token=?",
                       (body.token,)).fetchone()
    if not row or row["expires"] < datetime.datetime.utcnow().isoformat():
        conn.close()
        raise HTTPException(400, "That reset link is invalid or expired - request a new one.")
    salt = secrets.token_hex(16)
    conn.execute("UPDATE users SET pw_hash=?, salt=? WHERE id=?",
                 (hash_pw(body.password, salt), salt, row["user_id"]))
    conn.execute("DELETE FROM password_resets WHERE token=?", (body.token,))
    conn.execute("DELETE FROM sessions WHERE user_id=?", (row["user_id"],))
    conn.commit(); conn.close()
    return {"ok": True, "note": "Password updated - log in with the new one."}


# ----------------------------------------------------------------- csv export
@app.get("/api/export/{what}.csv")
def export_csv(what: str, request: Request):
    u = current_user(request)
    if not (u and u["plan"] == "pro"):
        raise HTTPException(402, "CSV export is a Pro feature.")
    import csv
    import io
    conn = db()
    if what == "tactics":
        rows = conn.execute("SELECT cat,tactic,cost,rel,ih,time,note FROM tactics").fetchall()
        header = ["Category", "Tactic", "Cost", "Relevance", "In-House", "Time-to-Impact", "Note"]
    elif what == "contacts":
        rows = conn.execute(
            "SELECT metro,category,scope,contacts,last_verified FROM contacts").fetchall()
        header = ["Metro", "Category", "Scope", "Contacts", "Last Verified"]
    else:
        conn.close()
        raise HTTPException(404, "Export tactics.csv or contacts.csv.")
    conn.close()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    for r in rows:
        w.writerow(list(r))
    return Response(buf.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={what}.csv"})


# ------------------------------------------------------------ verified badges
@app.get("/api/verified")
def verified(metro: str):
    conn = db()
    rows = [r["company"] for r in conn.execute(
        "SELECT company FROM verified_listings WHERE metro=?", (metro,))]
    conn.close()
    return rows


# ------------------------------------------------------------------ admin api
def require_admin(request: Request):
    if request.headers.get("x-admin-token") != ADMIN_TOKEN:
        raise HTTPException(403, "Admin token required.")


@app.get("/api/admin/overview")
def admin_overview(request: Request):
    require_admin(request)
    conn = db()
    users = conn.execute("SELECT COUNT(*) n FROM users").fetchone()["n"]
    pro = conn.execute("SELECT COUNT(*) n FROM users WHERE plan='pro'").fetchone()["n"]
    pending = conn.execute(
        "SELECT COUNT(*) n FROM claims WHERE status='pending'").fetchone()["n"]
    verify_pending = conn.execute(
        "SELECT COUNT(*) n FROM verification_queue WHERE status='pending'").fetchone()["n"]
    leads = conn.execute("SELECT COUNT(*) n FROM leads").fetchone()["n"]
    by_source = [dict(r) for r in conn.execute(
        "SELECT COALESCE(NULLIF(source,''),'direct') source, COUNT(*) n "
        "FROM leads GROUP BY 1 ORDER BY n DESC LIMIT 8")]
    fresh = [dict(r) for r in conn.execute(
        "SELECT last_verified, COUNT(*) rows_ FROM contacts GROUP BY last_verified")]
    conn.close()
    return {"users": users, "pro": pro, "mrr": pro * 49,
            "claims_pending": pending, "verify_pending": verify_pending, "leads": leads,
            "leads_by_source": by_source, "freshness": fresh}


@app.get("/api/admin/claims")
def admin_claims(request: Request):
    require_admin(request)
    conn = db()
    rows = [dict(r) for r in conn.execute("SELECT * FROM claims ORDER BY id DESC")]
    conn.close()
    return rows


class ClaimAction(BaseModel):
    action: str  # approve | reject


@app.post("/api/admin/claims/{claim_id}")
def admin_claim_action(claim_id: int, body: ClaimAction, request: Request):
    require_admin(request)
    if body.action not in ("approve", "reject"):
        raise HTTPException(400, "action must be approve or reject")
    conn = db()
    row = conn.execute("SELECT * FROM claims WHERE id=?", (claim_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "No such claim.")
    status = "approved" if body.action == "approve" else "rejected"
    conn.execute("UPDATE claims SET status=? WHERE id=?", (status, claim_id))
    if status == "approved":
        conn.execute("INSERT OR IGNORE INTO verified_listings(company,metro,claimed_by) "
                     "VALUES(?,?,?)", (row["company"], row["metro"], row["email"]))
    conn.commit(); conn.close()
    return {"ok": True, "status": status}


# ------------------------------------------------------- re-verification queue
# Populated by verify_contacts.py (run outside this sandbox - see that file's
# docstring). Findings sit here for a human to approve/reject in /admin;
# nothing here ever auto-overwrites a contact row unattended.
@app.get("/api/admin/verification-queue")
def admin_verification_queue(request: Request, status: str = "pending"):
    require_admin(request)
    conn = db()
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM verification_queue WHERE status=? ORDER BY id DESC", (status,))]
    conn.close()
    return rows


class VerificationAction(BaseModel):
    action: str  # approve | reject
    updated_contacts: str = ""  # optional: admin-edited replacement text


@app.post("/api/admin/verification-queue/{item_id}")
def admin_verification_action(item_id: int, body: VerificationAction, request: Request):
    require_admin(request)
    if body.action not in ("approve", "reject"):
        raise HTTPException(400, "action must be approve or reject")
    conn = db()
    row = conn.execute("SELECT * FROM verification_queue WHERE id=?", (item_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "No such queue item.")
    import datetime
    today = datetime.date.today().isoformat()
    if body.action == "approve":
        new_text = body.updated_contacts.strip() or row["old_contacts"]
        if row["contact_id"]:
            conn.execute(
                "UPDATE contacts SET contacts=?, last_verified=?, verified_by=? WHERE id=?",
                (new_text, today, f"re-verified via {row['provider']}", row["contact_id"]))
        conn.execute("UPDATE verification_queue SET status='approved', reviewed=? WHERE id=?",
                     (today, item_id))
    else:
        conn.execute("UPDATE verification_queue SET status='rejected', reviewed=? WHERE id=?",
                     (today, item_id))
    conn.commit(); conn.close()
    return {"ok": True, "status": "approved" if body.action == "approve" else "rejected"}


@app.get("/admin")
def admin_page():
    return FileResponse(os.path.join(HERE, "web", "admin.html"))


# ------------------------------------------------------------- vendor claims
@app.post("/api/claim")
def claim(body: Claim):
    if "@" not in body.email or not body.company.strip():
        raise HTTPException(400, "Company name and a valid email are required.")
    conn = db()
    conn.execute("INSERT INTO claims(company,metro,email,message) VALUES(?,?,?,?)",
                 (body.company.strip(), body.metro, body.email.strip(), body.message.strip()))
    conn.commit(); conn.close()
    return {"ok": True, "status": "pending",
            "note": "We'll verify ownership and email you a claim link."}


@app.get("/api/claims")
def claims_list(request: Request):
    """Admin-ish view for the demo: list filed claims."""
    conn = db()
    rows = [dict(r) for r in conn.execute(
        "SELECT company,metro,email,status,created FROM claims ORDER BY id DESC")]
    conn.close()
    return rows


# ------------------------------------------------------------------ frontend
@app.get("/")
def index():
    return FileResponse(os.path.join(HERE, "web", "index.html"))


# Programmatic SEO pages (build_seo_pages.py) served at /rates
_SEO_DIR = os.path.join(HERE, "seo")
if os.path.isdir(_SEO_DIR):
    from fastapi.staticfiles import StaticFiles
    app.mount("/rates", StaticFiles(directory=_SEO_DIR, html=True), name="rates")


if __name__ == "__main__":
    import uvicorn
    if not os.path.exists(DB):
        raise SystemExit("Run init_db.py first (needs data.json from export_data.py).")
    mode = "Stripe LIVE" if (STRIPE_KEY and PRICE_ID) else "mock subscription mode"
    print(f"AdAtlas API on http://localhost:8000  ({mode})")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
