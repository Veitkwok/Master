#!/usr/bin/env bash
# Verify the local pack and the Bot installation.
#
#   bash verify.sh
#   SKIP_INSTALLED=1 bash verify.sh
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DST="${MASTER_SKILL_HOME:-$HOME/agent-data/workflows}/finance-master"
WORKSPACE="${MASTER_WORKSPACE:-/workspace/master}"
SKILL_FIXED="$WORKSPACE/skill"
WORKER="$SKILL_FIXED/scripts/deepseek_analyze.py"
rc=0

echo "== verify: source =="
if command -v python3 >/dev/null 2>&1; then
  python3 "$ROOT/dev/check_pack.py" || rc=1
else
  echo "ERROR: python3 missing" >&2
  rc=1
fi

echo
echo "== verify: installed skill library =="
if [[ "${SKIP_INSTALLED:-0}" == "1" ]]; then
  echo "skipped (SKIP_INSTALLED=1)"
elif [[ -d "$SKILL_DST" ]]; then
  echo "found: $SKILL_DST"
  if command -v python3 >/dev/null 2>&1; then
    python3 "$ROOT/dev/check_pack.py" --installed "$SKILL_DST" || rc=1
  fi
else
  echo "WARN: skill library not found at $SKILL_DST (run install.sh)"
fi

echo
echo "== verify: fixed worker =="
if [[ -f "$WORKER" ]]; then
  echo "OK: $WORKER"
  if command -v python3 >/dev/null 2>&1; then
    MASTER_WORKSPACE="$WORKSPACE" MASTER_SKILL_ROOT="$SKILL_FIXED" \
      python3 "$WORKER" --selftest >/dev/null 2>&1 && echo "OK: --selftest runs" \
      || echo "WARN: --selftest returned non-zero (check key/files)"
  fi
else
  echo "ERROR: fixed worker missing at $WORKER (run install.sh)" >&2
  rc=1
fi
if [[ -f "$WORKSPACE/.secrets/deepseek.key" || -n "${DEEPSEEK_API_KEY:-}" ]]; then
  echo "OK: DeepSeek key present (file or env)"
else
  echo "WARN: no DeepSeek key yet (.secrets/deepseek.key / DEEPSEEK_API_KEY)"
fi

echo
echo "== verify: runtime dirs =="
for d in jobs out out/archive state/runs state/advice state/watchlists packs .secrets; do
  if [[ -d "$WORKSPACE/$d" ]]; then
    echo "OK: $WORKSPACE/$d"
  else
    echo "WARN: $WORKSPACE/$d missing (run install.sh)" >&2
  fi
done

echo
if [[ $rc -eq 0 ]]; then echo "verify: PASS"; else echo "verify: FAIL"; fi
exit $rc
