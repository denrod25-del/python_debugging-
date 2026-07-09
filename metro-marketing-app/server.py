#!/usr/bin/env python3
"""MetroStack API server (FastAPI + SQLite).

Production-shaped backend for the prototype:
  * auth: signup / login / logout with PBKDF2 password hashing + session tokens
  * subscription: plan lives on the user record, enforced SERVER-SIDE
      - free  -> 5 unlocked categories per market, 25 tactics per query, 10 quick wins
      - pro   -> everything
    /api/subscribe uses Stripe Checkout when STRIPE_SECRET_KEY is set,
    otherwise runs in mock mode (flips the plan directly) for local demo.
  * data: served from metrostack.db with last_verified on every contact row
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
DB = os.path.join(HERE, "metrostack.db")
STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")          # Pro $49/mo price
FREE_CATS = {"Outdoor / OOH", "Print", "Digital - Search & Display",
             "Local & Direct", "Partnership & Channel"}
FREE_TACTIC_CAP = 25
FREE_WINS_CAP = 10

app = FastAPI(title="MetroStack API")


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


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
    cur = conn.execute("INSERT INTO users(email,pw_hash,salt) VALUES(?,?,?)",
                       (email, hash_pw(creds.password, salt), salt))
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


if __name__ == "__main__":
    import uvicorn
    if not os.path.exists(DB):
        raise SystemExit("Run init_db.py first (needs data.json from export_data.py).")
    mode = "Stripe LIVE" if (STRIPE_KEY and PRICE_ID) else "mock subscription mode"
    print(f"MetroStack API on http://localhost:8000  ({mode})")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
