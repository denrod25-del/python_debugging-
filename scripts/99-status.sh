#!/usr/bin/env bash
# 99-status — print every deployed URL and the one manual step the user must do.

. "$(dirname "$0")/lib.sh"

if [[ ! -f "$STATE_FILE" ]]; then
  warn "No .deploy-state yet — nothing deployed. Run: bash deploy.sh"
  exit 0
fi

landing=$(state_get "url_landing")
app=$(state_get "url_app")
proxy=$(state_get "url_proxy")
origin=$(state_get "allowed_origin")

printf '\n'
printf '  Landing : %s\n' "${landing:-<not deployed>}"
printf '  App     : %s\n' "${app:-<not deployed>}"
printf '  Proxy   : %s\n' "${proxy:-<not deployed>}"
[[ -n "$proxy" ]]  && printf '  AI endpoint : %s/api/ai\n' "$proxy"
[[ -n "$origin" ]] && printf '  Proxy CORS origin : %s\n' "$origin"
printf '\n'

if [[ -n "$app" && -n "$proxy" ]]; then
  printf '\033[1mOne manual step remaining:\033[0m\n'
  printf '  Open  %s\n' "$app"
  printf '  Go to  Stats → AI endpoint\n'
  printf '  Paste  %s/api/ai\n' "$proxy"
  printf '  Save, then click "Test connection".\n\n'
else
  warn "Deploy incomplete — some URLs are missing. Re-run the failed phase."
fi
