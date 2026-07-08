#!/usr/bin/env bash
# 40-vercel-redeploy — force a new production deploy of the proxy so the
# env vars set in step 30 actually take effect.

. "$(dirname "$0")/lib.sh"

log "Redeploying proxy"
out=$(cd "$PROXY_REPO_NAME" && vercel_cli --prod --yes 2>&1)
url=$(printf '%s\n' "$out" | grep -oE 'https://[a-zA-Z0-9.-]+\.vercel\.app' | tail -1)
[[ -n "$url" ]] || die "Could not parse proxy URL after redeploy"

state_set "url_proxy" "$url"
ok "Proxy live at $url"
