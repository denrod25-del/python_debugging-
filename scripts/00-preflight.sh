#!/usr/bin/env bash
# 00-preflight — verify CLIs, config, and monorepo layout.

. "$(dirname "$0")/lib.sh"

log "Preflight"

# CLIs
missing=()
for cmd in git gh vercel jq; do
  command -v "$cmd" >/dev/null 2>&1 || missing+=("$cmd")
done
if (( ${#missing[@]} > 0 )); then
  die "Missing CLI(s): ${missing[*]}. Install and re-run."
fi
ok "CLIs present: git, gh, vercel, jq"

# gh auth
if ! gh auth status >/dev/null 2>&1; then
  die "GitHub CLI not authenticated. Run: gh auth login"
fi
ok "gh authenticated"

# vercel auth
if ! vercel_cli whoami >/dev/null 2>&1; then
  die "Vercel CLI not authenticated. Run: vercel login"
fi
ok "vercel authenticated ($(vercel_cli whoami 2>/dev/null))"

# .env
[[ -f .env ]] || die ".env not found. Copy .env.example → .env and fill in values."
ok ".env loaded"

# Required config
[[ -n "${GITHUB_USER:-}" ]]        || die "GITHUB_USER not set in .env"
[[ -n "${ANTHROPIC_API_KEY:-}" ]]  || die "ANTHROPIC_API_KEY not set in .env"
ok "Required config present"

# Subfolders
for d in "$LANDING_REPO_NAME" "$APP_REPO_NAME" "$PROXY_REPO_NAME"; do
  [[ -d "$d" ]] || die "Missing folder: $d"
done
ok "Sub-projects present: $LANDING_REPO_NAME, $APP_REPO_NAME, $PROXY_REPO_NAME"

ok "Preflight passed"
