#!/usr/bin/env bash
# Publish the Master/ pack to the distribution repo on GitHub.
#
# Run on the Mac monorepo (NOT on the Bot):
#   bash Master/dev/publish-to-github.sh
#   bash Master/dev/publish-to-github.sh <remote-url>
#
# It clones the remote (shallow), rsyncs Master/ over it, commits and pushes.
# Because the commit's parent is the remote HEAD, the push is a fast-forward,
# so the Bot can update with a plain `git pull` (no reset needed).
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

DEST="$TMP/repo"
if git -c credential.helper='!gh auth git-credential' clone --depth 1 "$REMOTE" "$DEST" 2>/dev/null; then
  echo "cloned existing history (fast-forward publish)"
else
  echo "remote empty/unreachable -> initialising a fresh repo"
  mkdir -p "$DEST"
  git -C "$DEST" init -q -b main
  git -C "$DEST" remote add origin "$REMOTE"
fi

rsync -a --delete \
  --exclude '.git' \
  --exclude '.tmp' \
  --exclude 'state' \
  --exclude 'out' \
  --exclude 'packs' \
  --exclude '.secrets' \
  --exclude 'jobs' \
  "$SRC/" "$DEST/"

cd "$DEST"
git add -A
VERSION="$(cat VERSION 2>/dev/null || echo unknown)"
if git diff --cached --quiet; then
  echo "no changes; nothing to publish"
  exit 0
fi
git -c user.name="Veitkwok" \
    -c user.email="veitkwok@users.noreply.github.com" \
    commit -q -m "Master pack v$VERSION (published $(date +%F\ %H:%M))"
git -c credential.helper='!gh auth git-credential' push origin HEAD:main
echo "published v$VERSION to $REMOTE (main, fast-forward)"
