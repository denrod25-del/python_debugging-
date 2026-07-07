// Python Debug Dojo — AI proxy as an Express server (reference only).
// Same request/response contract as pydojo-proxy. Runs anywhere Node runs;
// a Dockerfile is included. No external deps beyond Express.
//
// Env vars:
//   ANTHROPIC_API_KEY  (required)
//   ALLOWED_ORIGIN     (optional)  blank => "*"
//   ANTHROPIC_MODEL    (optional)
//   PORT               (optional)  default 8080

const express = require("express");

const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION = "2023-06-01";
const DEFAULT_MODEL = "claude-sonnet-5";
const DEFAULT_MAX_TOKENS = 1024;

const app = express();
app.use(express.json({ limit: "1mb" }));

function setCors(res) {
  const allow = (process.env.ALLOWED_ORIGIN || "").trim() || "*";
  res.set("Access-Control-Allow-Origin", allow);
  res.set("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.set("Access-Control-Allow-Headers", "Content-Type");
  res.set("Vary", "Origin");
}

app.options("/api/ai", (req, res) => { setCors(res); res.sendStatus(204); });

app.get("/health", (req, res) => res.json({ ok: true }));

app.post("/api/ai", async (req, res) => {
  setCors(res);
  const apiKey = (process.env.ANTHROPIC_API_KEY || "").trim();
  if (!apiKey) return res.status(500).json({ error: "Server misconfigured: ANTHROPIC_API_KEY not set." });

  const payload = req.body || {};
  let messages = payload.messages;
  if (!Array.isArray(messages) || messages.length === 0) {
    const prompt = typeof payload.prompt === "string" ? payload.prompt : "";
    if (!prompt.trim()) return res.status(400).json({ error: "Provide either 'messages' or a non-empty 'prompt'." });
    messages = [{ role: "user", content: prompt }];
  }

  const model =
    (typeof payload.model === "string" && payload.model.trim()) ||
    (process.env.ANTHROPIC_MODEL || "").trim() ||
    DEFAULT_MODEL;
  const maxTokens =
    Number.isFinite(payload.max_tokens) && payload.max_tokens > 0
      ? Math.min(Math.floor(payload.max_tokens), 4096)
      : DEFAULT_MAX_TOKENS;

  const body = { model, max_tokens: maxTokens, messages };
  if (typeof payload.system === "string" && payload.system.trim()) body.system = payload.system;

  try {
    const upstream = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": ANTHROPIC_VERSION,
      },
      body: JSON.stringify(body),
    });
    const data = await upstream.json().catch(() => null);
    if (!upstream.ok) {
      return res.status(upstream.status).json({ error: data?.error?.message || `Anthropic API error (${upstream.status})` });
    }
    const text = Array.isArray(data?.content)
      ? data.content.filter((b) => b.type === "text").map((b) => b.text).join("")
      : "";
    res.json({ text, model: data?.model || model, usage: data?.usage || null });
  } catch (e) {
    res.status(502).json({ error: "Failed to reach Anthropic API: " + (e?.message || e) });
  }
});

const port = process.env.PORT || 8080;
app.listen(port, () => console.log(`pydojo proxy listening on :${port}`));
