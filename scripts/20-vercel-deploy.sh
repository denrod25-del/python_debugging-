#!/usr/bin/env bash
# 20-vercel-deploy — first production deploy of each sub-project.
# `vercel --prod --yes` in an unlinked folder creates the project (named after
# the folder) and links it via the .vercel/ folder. Idempotent: re-running just
# ships a new production deployment and refreshes the URL in .deploy-state.

. "$(dirname "$0")/lib.sh"

deploy_folder() {
  local folder="$1" state_key="$2"
  log "→ deploying $folder"
  local out url
  out=$(cd "$folder" && vercel_cli --prod --yes 2>&1)
  url=$(printf '%s\n' "$out" | grep -oE 'https://[a-zA-Z0-9.-]+\.vercel\.app' | tail -1)
  if [[ -z "$url" ]]; then
    printf '%s\n' "$out" >&2
    die "Could not parse deployment URL for $folder"
  fi
  state_set "$state_key" "$url"
  ok "  $folder → $url"
}

log "Deploying to Vercel (first deploy creates each project)"
deploy_folder "$LANDING_REPO_NAME" "url_landing"
deploy_folder "$APP_REPO_NAME"     "url_app"
deploy_folder "$PROXY_REPO_NAME"   "url_proxy"

ok "Vercel deploy phase done — URLs saved to .deploy-state"
