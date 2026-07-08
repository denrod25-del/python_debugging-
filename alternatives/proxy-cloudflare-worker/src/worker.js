// Python Debug Dojo — AI proxy as a Cloudflare Worker (reference only).
// Same request/response contract as pydojo-proxy. Deploy with `wrangler deploy`.
//
// Secrets/vars:
//   ANTHROPIC_API_KEY  (required)  -> `wrangler secret put ANTHROPIC_API_KEY`
//   ALLOWED_ORIGIN     (optional)  -> [vars] in wrangler.toml; blank => "*"
//   ANTHROPIC_MODEL    (optional)  -> [vars] in wrangler.toml

const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION = "2023-06-01";
const DEFAULT_MODEL = "claude-sonnet-5";
const DEFAULT_MAX_TOKENS = 1024;

function cors(env) {
  const allow = (env.ALLOWED_ORIGIN || "").trim() || "*";
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
  };
}
function json(env, body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...cors(env) },
  });
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(env) });
    if (request.method !== "POST") return json(env, { error: "Method not allowed. Use POST." }, 405);

    const apiKey = (env.ANTHROPIC_API_KEY || "").trim();
    if (!apiKey) return json(env, { error: "Server misconfigured: ANTHROPIC_API_KEY not set." }, 500);

    let payload;
    try { payload = await request.json(); } catch { return json(env, { error: "Invalid JSON body." }, 400); }

    let messages = payload.messages;
    if (!Array.isArray(messages) || messages.length === 0) {
      const prompt = typeof payload.prompt === "string" ? payload.prompt : "";
      if (!prompt.trim()) return json(env, { error: "Provide either 'messages' or a non-empty 'prompt'." }, 400);
      messages = [{ role: "user", content: prompt }];
    }

    const model =
      (typeof payload.model === "string" && payload.model.trim()) ||
      (env.ANTHROPIC_MODEL || "").trim() ||
      DEFAULT_MODEL;
    const maxTokens =
      Number.isFinite(payload.max_tokens) && payload.max_tokens > 0
        ? Math.min(Math.floor(payload.max_tokens), 4096)
        : DEFAULT_MAX_TOKENS;

    const body = { model, max_tokens: maxTokens, messages };
    if (typeof payload.system === "string" && payload.system.trim()) body.system = payload.system;

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
      return json(env, { error: "Failed to reach Anthropic API: " + (e?.message || e) }, 502);
    }

    const data = await upstream.json().catch(() => null);
    if (!upstream.ok) {
      return json(env, { error: data?.error?.message || `Anthropic API error (${upstream.status})` }, upstream.status);
    }
    const text = Array.isArray(data?.content)
      ? data.content.filter((b) => b.type === "text").map((b) => b.text).join("")
      : "";
    return json(env, { text, model: data?.model || model, usage: data?.usage || null });
  },
};
