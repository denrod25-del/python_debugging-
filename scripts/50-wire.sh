#!/usr/bin/env bash
# 50-wire — wire the landing page to the deployed app + proxy, then redeploy it.
# Renders pydojo-landing/index.html from index.template.html with the real URLs,
# commits + pushes the landing repo, and ships a new production deploy.
# Idempotent: always re-renders from the template.

. "$(dirname "$0")/lib.sh"

APP_URL=$(state_get "url_app")
PROXY_URL=$(state_get "url_proxy")
[[ -n "$APP_URL" ]]   || die "url_app not in .deploy-state. Run 20-vercel-deploy.sh first."
[[ -n "$PROXY_URL" ]] || die "url_proxy not in .deploy-state. Run 20/40 first."

tpl="$LANDING_REPO_NAME/index.template.html"
out="$LANDING_REPO_NAME/index.html"
[[ -f "$tpl" ]] || die "Missing template: $tpl"

log "Wiring landing → app ($APP_URL), proxy ($PROXY_URL/api/ai)"
sed -e "s|__APP_URL__|$APP_URL|g" \
    -e "s|__PROXY_URL__|$PROXY_URL|g" \
    "$tpl" > "$out"
ok "  Rendered $out"

# Commit + push the landing sub-repo if it was initialised in step 10.
if [[ -d "$LANDING_REPO_NAME/.git" ]]; then
  ( cd "$LANDING_REPO_NAME" || exit 1
    git add -A
    if git diff --cached --quiet 2>/dev/null; then
      ok "  Landing repo already up to date"
    else
      git commit -m "Wire landing to deployed app URL" >/dev/null 2>&1 || exit 1
      if ! git push origin main >/dev/null 2>&1; then
        warn "  Normal push failed — trying --force-with-lease"
        git push origin main --force-with-lease || exit 1
      fi
      ok "  Pushed landing"
    fi
  ) || die "Failed to commit/push $LANDING_REPO_NAME"
else
  warn "  $LANDING_REPO_NAME has no .git — skipping push (run 10-github.sh to enable)"
fi

# Redeploy landing so the wired index.html goes live.
log "Redeploying landing"
out_deploy=$(cd "$LANDING_REPO_NAME" && vercel_cli --prod --yes 2>&1)
url=$(printf '%s\n' "$out_deploy" | grep -oE 'https://[a-zA-Z0-9.-]+\.vercel\.app' | tail -1)
[[ -n "$url" ]] || die "Could not parse landing URL after redeploy"

state_set "url_landing" "$url"
ok "Landing live at $url"
