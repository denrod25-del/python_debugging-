// Symbolic — AI proxy (Vercel Edge Function).
//
// Route:   POST /api/ai
// Purpose: keep the Anthropic API key server-side. The Symbolic app calls this
//          endpoint for its AI specialists; this function forwards to the
//          Anthropic Messages API. The key is NEVER sent to the browser.
//
// It supports BOTH streaming and non-streaming responses:
//   • { ..., "stream": true }  → the Anthropic SSE stream is piped straight
//     through as `text/event-stream` (the client renders tokens as they arrive).
//   • otherwise                → a single JSON reply { text, model, usage }.
//
// Env vars:
//   ANTHROPIC_API_KEY  (required)  — your Anthropic key
//   ALLOWED_ORIGIN     (optional)  — restrict CORS to one origin; blank => "*"
//   SYMBOLIC_MODEL     (optional)  — model id; blank => DEFAULT_MODEL below
//
// Request body (JSON):
//   { "messages": [{ "role": "user", "content": "…" }],
//     "system": "…", "max_tokens": 2048, "model": "…", "stream": true }
// A simple { "prompt": "…", "system": "…" } shape is also accepted.

export const config = { runtime: "edge" };

const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION = "2023-06-01";
// Symbolic's specialists are reasoning-heavy — default to the most capable Opus.
// Override per-deploy with SYMBOLIC_MODEL, or per-request with "model".
const DEFAULT_MODEL = "claude-opus-4-8";
const DEFAULT_MAX_TOKENS = 2048;
const MAX_MAX_TOKENS = 8192;

function env(name) {
  return (globalThis.process?.env?.[name] || "").trim();
}

function corsHeaders() {
  // SECURITY: with ALLOWED_ORIGIN unset this defaults to "*", i.e. an open,
  // unauthenticated proxy any site can call to spend your Anthropic key. Fine
  // for local/dev; in production set ALLOWED_ORIGIN to your app's origin.
  const allow = env("ALLOWED_ORIGIN") || "*";
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
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders() });
  }
  if (req.method !== "POST") {
    return json({ error: "Method not allowed. Use POST." }, 405);
  }

  const apiKey = env("ANTHROPIC_API_KEY");
  if (!apiKey) {
    return json({ error: "Server misconfigured: ANTHROPIC_API_KEY not set." }, 500);
  }

  let payload;
  try {
    payload = await req.json();
  } catch {
    return json({ error: "Invalid JSON body." }, 400);
  }

  // Normalise the accepted request shapes into Anthropic's format.
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
    env("SYMBOLIC_MODEL") ||
    env("ANTHROPIC_MODEL") ||
    DEFAULT_MODEL;

  const maxTokens =
    Number.isFinite(payload.max_tokens) && payload.max_tokens > 0
      ? Math.min(Math.floor(payload.max_tokens), MAX_MAX_TOKENS)
      : DEFAULT_MAX_TOKENS;

  const stream = payload.stream === true;

  const body = { model, max_tokens: maxTokens, messages, stream };
  if (typeof payload.system === "string" && payload.system.trim()) {
    body.system = payload.system;
  }

  const controller = new AbortController();
  // Streaming keeps the connection alive with token deltas, so it can run
  // longer than a single blocking call. Give it generous headroom.
  const timeoutMs = stream ? 55000 : 30000;
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

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
      signal: controller.signal,
    });
  } catch (e) {
    clearTimeout(timeout);
    const msg =
      e?.name === "AbortError"
        ? "Anthropic API request timed out."
        : "Failed to reach Anthropic API: " + (e?.message || e);
    return json({ error: msg }, 502);
  }

  // Upstream error: surface it as JSON regardless of the requested mode.
  if (!upstream.ok) {
    clearTimeout(timeout);
    const data = await upstream.json().catch(() => null);
    const msg = data?.error?.message || `Anthropic API error (${upstream.status})`;
    return json({ error: msg }, upstream.status);
  }

  // Streaming: pipe the Anthropic SSE straight through to the client.
  if (stream) {
    // The response headers are in, so the connection is healthy — clear the
    // connect-timeout guard now. Leaving it armed against the fetch signal
    // would abort a legitimately long generation mid-stream. Overall stream
    // duration is bounded by the platform's function limit.
    clearTimeout(timeout);
    return new Response(upstream.body, {
      status: 200,
      headers: {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-cache, no-transform",
        Connection: "keep-alive",
        ...corsHeaders(),
      },
    });
  }

  // Non-streaming: collapse the assistant text blocks into one string.
  clearTimeout(timeout);
  const data = await upstream.json().catch(() => null);
  const text = Array.isArray(data?.content)
    ? data.content.filter((b) => b.type === "text").map((b) => b.text).join("")
    : "";
  return json({ text, model: data?.model || model, usage: data?.usage || null });
}
