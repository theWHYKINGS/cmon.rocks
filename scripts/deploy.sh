#!/usr/bin/env bash
#
# deploy.sh — publish the current index.html to GitHub Pages.
#
# This commits whatever is in the working tree (normally a freshly pulled
# index.html from the Claude Design CMON project) and pushes it to
# github.com/theWHYKINGS/cmon.rocks, which GitHub Pages then serves at
# https://www.cmon.rocks.
#
# Usage:
#   scripts/deploy.sh                 # commits with a timestamped message
#   scripts/deploy.sh "Update hero"   # commits with a custom message
#
# The *pull* step (fetching the latest source out of Claude Design) is done by
# Claude via the authenticated browser session — see scripts/pull-from-design.md.
# This script only handles the publish half of the loop.

set -euo pipefail

cd "$(dirname "$0")/.."          # repo root
export PATH="$HOME/.local/bin:$PATH"   # local gh install

MSG="${1:-Update site — $(date '+%Y-%m-%d %H:%M')}"

# No post-processing yet — the CMON design is hosted as-is (client-rendered
# source + support.js). NOTE: real Impressum/Datenschutz/AGB content is still
# missing (footer links are empty #anchors) and must be added before the site
# is public — German Impressumspflicht. See scripts/pull-from-design.md.

if [ -z "$(git status --porcelain)" ]; then
  echo "Nothing changed — working tree is clean. Nothing to deploy."
  exit 0
fi

echo "Staging changes…"
git add -A
git status --short

echo "Committing: $MSG"
git commit -q -m "$MSG

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"

echo "Pushing to GitHub…"
git push -q origin main

# GitHub Pages does not reliably start a build on push for these repos (observed
# repeatedly on the academy repo: the commit lands, no build is queued, the live
# site keeps serving the previous version). Ask for one explicitly — harmless if
# Pages already queued its own.
echo "Requesting a Pages build…"
gh api -X POST repos/theWHYKINGS/cmon.rocks/pages/builds --jq '.status' || \
  echo "  ! could not request a build — check https://github.com/theWHYKINGS/cmon.rocks/settings/pages"

echo
echo "✅ Pushed. GitHub Pages will rebuild in ~1 minute."
echo "   Live:  https://www.cmon.rocks"
echo "   Build: https://github.com/theWHYKINGS/cmon.rocks/actions"
