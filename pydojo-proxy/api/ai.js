// Python Debug Dojo — AI proxy (Vercel Edge Function).
//
// Route:   POST /api/ai
// Purpose: keep the Anthropic API key server-side. The dojo app calls this
//          endpoint; this function forwards to the Anthropic Messages API and
//          returns the assistant text. The key is NEVER sent to the browser.
//
// Env vars (set by scripts/30-vercel-env.sh):
//   ANTHROPIC_API_KEY  (required)  — your Anthropic key
//   ALLOWED_ORIGIN     (optional)  — restrict CORS to one origin; blank => "*"
//   ANTHROPIC_MODEL    (optional)  — model id; blank => DEFAULT_MODEL below
//
// Request body (JSON), either shape works:
//   { "prompt": "…", "system": "…" }                      // simple
//   { "messages": [{ "role": "user", "content": "…" }] }  // full control
// Optional: "max_tokens" (number), "model" (string, overrides env default).
//
// Response: { "text": "…", "model": "…", "usage": {…} }  on success
//           { "error": "…" }                              on failure

export const config = { runtime: "edge" };

const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION = "2023-06-01";
// A current, widely-available default. Override with ANTHROPIC_MODEL.
const DEFAULT_MODEL = "claude-sonnet-5";
const DEFAULT_MAX_TOKENS = 1024;

function corsHeaders() {
  const allow = (globalThis.process?.env?.ALLOWED_ORIGIN || "").trim() || "*";
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
  };
}

function json(body, status = 200, extra = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders(), ...extra },
  });
}

export default async function handler(req) {
  // CORS preflight.
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders() });
  }
  if (req.method !== "POST") {
    return json({ error: "Method not allowed. Use POST." }, 405);
  }

  const apiKey = (globalThis.process?.env?.ANTHROPIC_API_KEY || "").trim();
  if (!apiKey) {
    return json({ error: "Server misconfigured: ANTHROPIC_API_KEY not set." }, 500);
  }

  let payload;
  try {
    payload = await req.json();
  } catch {
    return json({ error: "Invalid JSON body." }, 400);
  }

  // Normalise the two accepted request shapes into Anthropic's format.
  let messages = payload.messages;
  if (!Array.isArray(messages) || messages.length === 0) {
    const prompt = typeof payload.prompt === "string" ? payload.prompt : "";
    if (!prompt.trim()) {
      return json({ error: "Provide either 'messages' or a non-empty 'prompt'." }, 400);
    }
    messages = [{ role: "user", content: prompt }];
  }

  const model =
    (typeof payload.model === "string" && payload.model.trim()) ||
    (globalThis.process?.env?.ANTHROPIC_MODEL || "").trim() ||
    DEFAULT_MODEL;

  const maxTokens =
    Number.isFinite(payload.max_tokens) && payload.max_tokens > 0
      ? Math.min(Math.floor(payload.max_tokens), 4096)
      : DEFAULT_MAX_TOKENS;

  const body = { model, max_tokens: maxTokens, messages };
  if (typeof payload.system === "string" && payload.system.trim()) {
    body.system = payload.system;
  }

  let upstream;
  try {
    upstream = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": ANTHROPIC_VERSION,
      },
      body: JSON.stringify(body),
    });
  } catch (e) {
    return json({ error: "Failed to reach Anthropic API: " + (e?.message || e) }, 502);
  }

  const data = await upstream.json().catch(() => null);
  if (!upstream.ok) {
    const msg = data?.error?.message || `Anthropic API error (${upstream.status})`;
    return json({ error: msg }, upstream.status);
  }

  // Concatenate all text blocks from the assistant response.
  const text = Array.isArray(data?.content)
    ? data.content.filter((b) => b.type === "text").map((b) => b.text).join("")
    : "";

  return json({ text, model: data?.model || model, usage: data?.usage || null });
}
