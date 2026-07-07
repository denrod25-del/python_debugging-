#!/usr/bin/env bash
# 30-vercel-env — set required env vars on the proxy project.
# Idempotent: removes existing vars first, then re-adds.

. "$(dirname "$0")/lib.sh"

APP_URL=$(state_get "url_app")
[[ -n "$APP_URL" ]] || die "url_app not in .deploy-state. Run 20-vercel-deploy.sh first."

# Default ALLOWED_ORIGIN to the app's Vercel URL if user didn't set one.
: "${ALLOWED_ORIGIN:=$APP_URL}"

set_env() {
  local name="$1" value="$2" sensitive_flag="${3:-}"

  # Remove existing value (silently ignore if not present).
  ( cd "$PROXY_REPO_NAME" && vercel_cli env rm "$name" production --yes >/dev/null 2>&1 || true )

  # Add — value comes from stdin.
  local extra=()
  [[ "$sensitive_flag" == "sensitive" ]] && extra+=(--sensitive)
  ( cd "$PROXY_REPO_NAME" && printf '%s' "$value" | vercel_cli env add "$name" production "${extra[@]}" >/dev/null )
  ok "  Set $name (production)"
}

log "Setting proxy env vars"
set_env "ANTHROPIC_API_KEY" "$ANTHROPIC_API_KEY" "sensitive"
set_env "ALLOWED_ORIGIN"    "$ALLOWED_ORIGIN"
state_set "allowed_origin" "$ALLOWED_ORIGIN"

ok "Vercel env phase done — proxy will pick these up on next deploy"
