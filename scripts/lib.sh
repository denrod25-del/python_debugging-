#!/usr/bin/env bash
# Shared helpers. Every script in this folder sources this file.
# NOT executed directly.

set -euo pipefail

# Resolve monorepo root (parent of scripts/).
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Load config.
if [[ -f .env ]]; then
  set -a
  # shellcheck source=/dev/null
  . .env
  set +a
fi

# Defaults.
: "${LANDING_REPO_NAME:=pydojo-landing}"
: "${APP_REPO_NAME:=pydojo-app}"
: "${PROXY_REPO_NAME:=pydojo-proxy}"
: "${VERCEL_SCOPE:=}"

STATE_FILE="$REPO_ROOT/.deploy-state"

# Pretty output.
log() { printf "\033[1;34m▸\033[0m %s\n" "$*" >&2; }
ok()  { printf "\033[1;32m✓\033[0m %s\n" "$*" >&2; }
warn(){ printf "\033[1;33m!\033[0m %s\n" "$*" >&2; }
die() { printf "\033[1;31m✗\033[0m %s\n" "$*" >&2; exit 1; }

# vercel with optional --scope flag baked in.
vercel_cli() {
  if [[ -n "$VERCEL_SCOPE" ]]; then
    vercel --scope "$VERCEL_SCOPE" "$@"
  else
    vercel "$@"
  fi
}

# State: read/write key=value pairs in .deploy-state.
state_get() {
  local key="$1"
  [[ -f "$STATE_FILE" ]] || { echo ""; return; }
  awk -F= -v k="$key" '$1==k{sub(/^[^=]*=/,""); print; exit}' "$STATE_FILE"
}
state_set() {
  local key="$1" value="$2"
  touch "$STATE_FILE"
  # Remove any existing line for the key, then append.
  local tmp
  tmp=$(mktemp)
  awk -F= -v k="$key" '$1!=k' "$STATE_FILE" > "$tmp"
  echo "$key=$value" >> "$tmp"
  mv "$tmp" "$STATE_FILE"
}

# Return the production URL of a Vercel project deployed from the given folder.
vercel_prod_url() {
  local folder="$1"
  ( cd "$folder" && vercel_cli inspect 2>/dev/null || true ) \
    | grep -oE 'https://[a-zA-Z0-9.-]+' \
    | head -1
}
