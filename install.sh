#!/usr/bin/env bash
# Install / update the finance-master Master pack on a Grok Bot computer.
#
#   bash install.sh
#
# What it does:
#   1. copies the skill into the Bot skill library (for the "/" menu);
#   2. copies the skill into /workspace/master/skill (stable path for the
#      fixed DeepSeek worker command — do not change it after approvals are set);
#   3. creates jobs/ out/ .secrets/ state/ under /workspace/master.
#
# Env overrides:
#   MASTER_WORKSPACE   work root        (default: /workspace/master)
#   MASTER_SKILL_HOME  skills library   (default: $HOME/agent-data/workflows)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="$ROOT/skills/finance-master"
SKILL_HOME="${MASTER_SKILL_HOME:-$HOME/agent-data/workflows}"
SKILL_DST="$SKILL_HOME/finance-master"
WORKSPACE="${MASTER_WORKSPACE:-/workspace/master}"

if [[ "$WORKSPACE" == /workspace/* ]] && [[ ! -w /workspace ]] 2>/dev/null; then
  echo "WARN: /workspace not writable, falling back to $HOME/master" >&2
  WORKSPACE="$HOME/master"
fi
SKILL_FIXED="$WORKSPACE/skill"
JOB="$WORKSPACE/jobs/current.json"

echo "== finance-master install =="
echo "repo:        $ROOT"
echo "skill lib:   $SKILL_DST"
echo "fixed copy:  $SKILL_FIXED   (worker command path)"
echo "work root:   $WORKSPACE"

if [[ ! -f "$SKILL_SRC/SKILL.md" ]]; then
  echo "ERROR: skill source missing: $SKILL_SRC" >&2
  exit 1
fi

# 1) Bot skill library (used by "/" + description routing)
mkdir -p "$SKILL_HOME"
rm -rf "$SKILL_DST"
cp -R "$SKILL_SRC" "$SKILL_DST"
echo "skill library copied: $(find "$SKILL_DST" -type f | wc -l | tr -d ' ') files"

# 2) stable copy for the fixed worker command (never changes path)
mkdir -p "$WORKSPACE"
rm -rf "$SKILL_FIXED"
cp -R "$SKILL_SRC" "$SKILL_FIXED"
echo "fixed skill copy: $(find "$SKILL_FIXED" -type f | wc -l | tr -d ' ') files"

# 3) runtime dirs (persist outside the skill)
mkdir -p "$WORKSPACE"/{jobs,out/archive,state/{runs,advice,watchlists},packs}
mkdir -p "$WORKSPACE/.secrets"
chmod 700 "$WORKSPACE/.secrets" "$WORKSPACE/state" 2>/dev/null || true
chmod 700 "$WORKSPACE"/out 2>/dev/null || true
if [[ ! -f "$JOB" ]]; then
  printf '{"schema":"master.deepseek.job/v1","job_id":"","mode":"routine","asof":"","pack":{}}\n' > "$JOB"
fi
echo "runtime dirs ready: $WORKSPACE/{jobs,out,state,packs,.secrets}"

# 4) structural check
if command -v python3 >/dev/null 2>&1; then
  python3 "$ROOT/dev/check_pack.py" --installed "$SKILL_DST" || {
    echo "WARN: check_pack reported issues (see above)" >&2
  }
else
  echo "WARN: python3 not found; skipping structural check" >&2
fi

cat <<EOF

安装完成。下一步（顺序很重要）：
1. 放 DeepSeek key（二选一）：
   echo '<key>' > $WORKSPACE/.secrets/deepseek.key && chmod 600 $WORKSPACE/.secrets/deepseek.key
   # 或使用 Bot secret 环境变量 DEEPSEEK_API_KEY
2. 在有人在场的对话里，手动跑一次固定命令并 Always allow：
   cd $WORKSPACE && /usr/bin/python3 -I -B $SKILL_FIXED/scripts/deepseek_analyze.py --selftest
   然后手动跑一次真实分析（先用 Test job），批准并生成 Allow 规则。
3. 按 $ROOT/runtime/routine-setup.md 建 5 条 routine。
4. Approvals：Auto Review；watchlist 写/下单/邮件 = Ask first；
   固定 worker 命令 = Allow automatically（见技能内 runtime/approvals.md）。
5. 首次自检（Bot 对话）："按 finance-master 技能读一次我的 IBKR 持仓和 watchlist"

固定 worker 命令（routine 里逐字使用，不要改）：
   /usr/bin/python3 -I -B $SKILL_FIXED/scripts/deepseek_analyze.py

日常更新：cd $ROOT && git pull && bash install.sh
EOF
