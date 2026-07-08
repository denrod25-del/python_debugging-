#!/usr/bin/env bash
# 10-github — create GitHub repos for each sub-project and push their contents.
# Idempotent: safe to re-run. Skips repo creation if already exists, force-pushes
# only if history diverged from a prior deploy.

. "$(dirname "$0")/lib.sh"

push_folder() {
  local folder="$1" repo_name="$2"
  local slug="${GITHUB_USER}/${repo_name}"

  log "→ $folder → github:$slug"

  # Create GitHub repo if it doesn't exist yet.
  if ! gh repo view "$slug" >/dev/null 2>&1; then
    gh repo create "$slug" --private --description "Python Debug Dojo — $folder" >/dev/null
    ok "  Created private repo $slug"
  else
    ok "  Repo $slug already exists"
  fi

  # Init local git if needed.
  ( cd "$folder"

    if [[ ! -d .git ]]; then
      git init -b main >/dev/null
      ok "  Initialized git in $folder"
    fi

    # Ensure a git identity is set (Vercel git-push requires it). gh returns a
    # null/empty email for accounts without a public email, so fall back to a
    # noreply address whenever the resolved value is empty.
    if ! git config user.name >/dev/null 2>&1; then
      git config user.name "$(gh api user --jq '.login' 2>/dev/null || echo "$GITHUB_USER")"
    fi
    if ! git config user.email >/dev/null 2>&1; then
      gh_email="$(gh api user --jq '.email // empty' 2>/dev/null || true)"
      [ -n "$gh_email" ] || gh_email="${GITHUB_USER}@users.noreply.github.com"
      git config user.email "$gh_email"
    fi

    # Point origin at HTTPS URL (gh auth token handles the push).
    local remote_url="https://github.com/${slug}.git"
    if git remote get-url origin >/dev/null 2>&1; then
      git remote set-url origin "$remote_url"
    else
      git remote add origin "$remote_url"
    fi

    git add -A
    if ! git diff --cached --quiet 2>/dev/null || [[ -z "$(git rev-parse -q --verify HEAD 2>/dev/null || echo)" ]]; then
      git commit -m "Deploy $(date -u +'%Y-%m-%dT%H:%M:%SZ')" >/dev/null 2>&1 \
        || die "  Commit failed in $folder (check git user.name/user.email)"
      ok "  Committed changes"
    else
      ok "  Nothing to commit"
    fi

    # Push. Try normal push first; fall back to force-with-lease if remote diverged.
    if ! git push -u origin main >/dev/null 2>&1; then
      warn "  Normal push failed — trying --force-with-lease"
      git push -u origin main --force-with-lease
    fi
    ok "  Pushed to $slug"
  )
}

log "Pushing to GitHub"
push_folder "$LANDING_REPO_NAME" "$LANDING_REPO_NAME"
push_folder "$APP_REPO_NAME"     "$APP_REPO_NAME"
push_folder "$PROXY_REPO_NAME"   "$PROXY_REPO_NAME"

state_set "github_landing" "https://github.com/${GITHUB_USER}/${LANDING_REPO_NAME}"
state_set "github_app"     "https://github.com/${GITHUB_USER}/${APP_REPO_NAME}"
state_set "github_proxy"   "https://github.com/${GITHUB_USER}/${PROXY_REPO_NAME}"

ok "GitHub phase done"
