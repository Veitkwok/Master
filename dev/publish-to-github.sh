#!/usr/bin/env bash
# Publish the Master/ pack to the distribution repo on GitHub.
#
# Run this on the Mac monorepo (NOT on the Bot):
#   bash Master/dev/publish-to-github.sh
#   bash Master/dev/publish-to-github.sh <remote-url>
#
# It copies Master/ into a temp dir (excluding runtime state/secrets), commits,
# and force-pushes `main` to the distribution repo. The Bot installs by cloning
# that repo and running install.sh — see README.md.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC="$MONO_ROOT/Master"
REMOTE="${1:-https://github.com/Veitkwok/Master.git}"

if [[ ! -f "$SRC/skills/finance-master/SKILL.md" ]]; then
  echo "ERROR: run from the finance-master-skill-build monorepo (Master/ not found)" >&2
  exit 1
fi

TMP="$MONO_ROOT/.publish-tmp.$$"
rm -rf "$TMP"
mkdir -p "$TMP"
trap 'rm -rf "$TMP"' EXIT

rsync -a \
  --exclude '.git' \
  --exclude '.tmp' \
  --exclude 'state' \
  --exclude 'out' \
  --exclude 'packs' \
  --exclude '.secrets' \
  --exclude 'jobs' \
  "$SRC/" "$TMP/"

cd "$TMP"
git init -q -b main
git add -A
VERSION="$(cat VERSION 2>/dev/null || echo unknown)"
git -c user.name="Veitkwok" \
    -c user.email="veitkwok@users.noreply.github.com" \
    commit -q -m "Master pack v$VERSION (published $(date +%F\ %H:%M))"
git -c credential.helper='!gh auth git-credential' push "$REMOTE" main --force

echo "published v$VERSION to $REMOTE (main)"
