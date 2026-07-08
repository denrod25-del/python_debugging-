#!/usr/bin/env bash
# Python Debug Dojo — one-command deploy orchestrator.
# Runs each phase in order. Every phase is idempotent, so if one fails you can
# fix the cause and re-run either this whole script or just the failed phase
# (see scripts/ and CLAUDE.md).
set -euo pipefail
cd "$(dirname "$0")"

echo "Python Debug Dojo — full deploy"
echo "================================"

bash scripts/00-preflight.sh
bash scripts/10-github.sh
bash scripts/20-vercel-deploy.sh
bash scripts/30-vercel-env.sh
bash scripts/40-vercel-redeploy.sh
bash scripts/50-wire.sh
bash scripts/99-status.sh

echo
echo "Done."
