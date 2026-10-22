#!/usr/bin/env python3
"""Normalizer for the vendored finance-master engine (Master v1).

Run from the Master/ repo root:

    python3 dev/vendor/normalize_engine.py

What it does (idempotent, exact-string replacements only):

1. runtime-boundary sentence patches (the whitelist listed in PATCHES);
2. cross-tree paths -> paths relative to the file that mentions them;
3. legacy IBKR / X tool names -> capability labels (the Bot connector
   discovers real tool names at runtime);
4. per-file legacy-word cleanup (cache / monorepo leftovers).

The method core (confidence contract, engine steps, method library,
valuation / trap / ETF method bodies) is intentionally untouched.
"""

from __future__ import annotations

import re
import sys
from os.path import relpath as _relpath
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # Master/
SKILL = ROOT / "skills" / "finance-master"
ENGINE = SKILL / "references" / "engine"

# ---------------------------------------------------------------------------
# 1. exact runtime-boundary sentence patches (applied before path rewriting)
# ---------------------------------------------------------------------------
PATCHES: list[tuple[str, str, str]] = [
    # ---- sherlock/GUIDE.md -------------------------------------------------
    ("sherlock/GUIDE.md",
     "> **Sole orchestrator** for this copy under `Master/finance-master/`. US equities/ETFs. Runtime: **Grok Bot**.",
     "> **Sole orchestrator** of the vendored engine. US equities/ETFs. Runtime: **Grok Bot**, called by the `finance-master` skill entry."),
    ("sherlock/GUIDE.md",
     "> Advice card, accounts, watchlists, and Schwab reads: `Master/references/`. Those files win when this text still mentions `lists/`, `cache/`, Scout, or 「禁止该买」.",
     "> The skill entry wraps this engine: advice card, accounts, watchlists, state and Schwab reads live in the skill entry (`SKILL.md` + `references/`). When this engine still mentions `cache/`, `lists/`, Scout or 「禁止该买」, the entry's precedence table wins."),
    ("sherlock/GUIDE.md",
     "**Boot:** §0 → §0.2b cache log → §0.2c",
     "**Boot:** §0 → §0.2b no-cache marker → §0.2c"),
    ("sherlock/GUIDE.md",
     "KOL accounts: `Master/references/discovery.md`. `x-advanced-research/references/key-accounts.md` only points there.",
     "KOL accounts: the skill entry's accounts contract (`references/contracts/accounts.md`). This engine never keeps a second account list."),
    ("sherlock/GUIDE.md",
     "Protocol: `Master/references/memory.md`. Use the Bot's Hindsight connector and bank `sherlock`. Do not call `localhost:8888`. Do not run `scripts/sherlock-ingest-case.py`. Do not ingest into `hermes`.",
     "Protocol: `references/contracts/memory.md`. Use the Bot's Hindsight connector and bank `sherlock`. Never call a localhost API and never run ingest scripts from the old monorepo."),
    ("sherlock/GUIDE.md",
     "After the advice card is final, retain the short case in `Master/references/memory.md`. Scout heat is not a chain.",
     "After the advice card is final, retain the short case through the Hindsight connector into bank `sherlock` (see `references/contracts/memory.md`). Social heat is not a chain."),
    ("sherlock/GUIDE.md",
     "**Tiers:** SESSION_CACHE fresh → REUSE; cache HIT → digest + live price; IBKR if available (min calls);",
     "**Tiers:** SESSION_CACHE fresh → REUSE; this turn's IBKR pack; Hindsight recall; IBKR if available (min calls);"),
    ("sherlock/GUIDE.md",
     "**IBKR quotes (default research):** `search_contracts` (exact US SYM) · `get_price_snapshot` · `get_price_history` (daily / FIVE_MINS) · `get_option_parameters`/`get_option_data` · `get_company_themes`/`get_company_connections` · `search_futures`.",
     "**IBKR quotes (default research):** contract resolve (exact US SYM) · last/quote snapshot · daily / FIVE_MINS history · option chain · themes / connections · futures search."),
    ("sherlock/GUIDE.md",
     "**Account reads (Master routines and any advice card):** IBKR positions and balances.",
     "**Account reads (any routine and any advice card):** IBKR positions and balances."),
    ("sherlock/GUIDE.md",
     "**Orders:** do not call `create_order_instruction`, `delete_order_instruction`, or `get_order_instructions` unless the user asks to stage a draft.",
     "**Orders:** never call an IBKR draft/order tool unless the user asks to stage a draft."),
    ("sherlock/GUIDE.md",
     "| 风口 / 观察候选 / KOL routine | Brain **§8.3**（standard）+ the pack；不自动跑 serenity/deep | 自动写观察列表；打开 Balder / Serenity / Koltracker 网站 |",
     "| 风口 / 观察候选 / KOL routine | Brain **§8.3**（standard）+ the pack，随后进技能入口的建议卡判定 | 自动写观察列表；打开 Balder / Serenity / Koltracker 网站 |"),
    ("sherlock/GUIDE.md",
     "**§11:** buy/safety → full-engine §6/§10, then `Master/references/advice.md`;",
     "**§11:** buy/safety → full-engine §6/§10, then the skill entry's advice-card contract;"),
    ("sherlock/GUIDE.md",
     "*Sherlock v4.6.8 inside Master · Grok Bot · omitted mode standard · no live submit*",
     "*Sherlock v4.6.8 · vendored engine · Grok Bot · omitted mode standard · no live submit*"),
    # ---- sherlock/references/full-engine.md --------------------------------
    ("sherlock/references/full-engine.md",
     "Full page: `Master/docs/reference/research-bias-checklist.md` — **do not** paste it.",
     "Full page: `../../docs/reference/research-bias-checklist.md` — **do not** paste it."),
    ("sherlock/references/full-engine.md",
     "### 9.1 Tree\n\n```\nUser request",
     "### 9.1 Tree\n\n> **Bot routines do not start this tree.** They follow the skill entry's runbooks: KOL posts → data pack → engine analysis → advice card. This tree applies when the user names desk-style research.\n\n```\nUser request"),
    ("sherlock/references/full-engine.md",
     "- Read the live book from `Master/references/data-plane.md`.  \n- Size a new buy only after `Master/references/advice.md`, and only if the user states a cash figure.  \n- Detail: `etf/references/user-capital-policy.md`. Grouping: `Master/references/book-and-overlaps.md`.",
     "- Read the live book from `../../contracts/data-pack.md`.  \n- Size a new buy only after the skill entry's advice card, and only if the user states a cash figure.  \n- Detail: `../modules/etf/references/user-capital-policy.md`. Grouping: `../../contracts/book-and-overlaps.md`."),
    ("sherlock/references/full-engine.md",
     "No L2 skip-ahead on that chain. Master KOL routines do not start this DAG. They use `Master/references/discovery.md`, then valuation and trap. `serenity-skill` and `deep-analysis` run when the user names them.",
     "No L2 skip-ahead on that chain. Bot routines do not start this DAG. They use the skill entry's runbooks and accounts contract, then valuation and trap. `serenity` and `deep-analysis` run only when the user names them."),
    ("sherlock/references/full-engine.md",
     "1. Veto result — a pass may become the card in `Master/references/advice.md`. A pass is not an order. Orange or red trap does not pass.",
     "1. Veto result — a pass may become the advice card defined by the skill entry. A pass is not an order. Orange or red trap does not pass."),
    ("sherlock/references/full-engine.md",
     "**skill must be allowlisted for mode_effective** · Brain merges cache.",
     "**skill must be allowlisted for mode_effective** · Brain merges SESSION_CACHE."),
    ("sherlock/references/full-engine.md",
     "> **§H.6 re-grade lives in `SKILL.md`.**",
     "> **§H.6 re-grade lives in `GUIDE.md`.**"),
    # ---- sherlock/references/data-pack-schema.md --------------------------
    ("sherlock/references/data-pack-schema.md",
     "**Master routines:** the gather format is `Master/references/data-plane.md`. Sherlock consumes that pack as this DATA_PACK. Do not keep a second analysis. Positions are already in the pack. L2 and DeepSeek do not call account tools themselves.",
     "**Bot routines:** the gather format is the skill entry's data-pack contract. Sherlock consumes that pack as this DATA_PACK. Do not keep a second analysis. Positions are already in the pack. L2 and the DeepSeek worker do not call account tools themselves."),
    ("sherlock/references/data-pack-schema.md",
     "**Master account reads** are `Master/references/data-plane.md`, not an L2 call.",
     "**Bot account reads** are defined by the skill entry's data-pack contract, not an L2 call."),
    ("sherlock/references/data-pack-schema.md",
     "sources_used: [IBKR, WEB, X, CACHE]",
     "sources_used: [IBKR, WEB, X]"),
    ("sherlock/references/data-pack-schema.md",
     "**L2 + DATA_PACK:** quotes and structure only — `search_contracts`, `get_price_snapshot`, `get_price_history`, option parameters/data, `get_company_themes`, `get_company_connections`, `search_futures`.",
     "**L2 + DATA_PACK:** quotes and structure only — contract resolve, quote snapshot, history bars, option chain, themes/connections, futures search."),
    # ---- banned-patterns.yaml --------------------------------------------
    ("sherlock/references/banned-patterns.yaml",
     "# Orders stay forbidden. Position reads are required by Master/references/data-plane.md.",
     "# Orders stay forbidden. Position reads are required by the skill entry's data-pack contract."),
    # ---- confidence examples / contract ----------------------------------
    ("sherlock/references/confidence-examples.md",
     "**Not a chain:** monorepo `cache/` digest, Scout heat, invented valuation bands.",
     "**Not a chain:** a research-cache digest (this pack has none), social heat, invented valuation bands."),
    ("sherlock/references/confidence-examples.md",
     "### Example — ETF sleeve lite B (issuer + optional IBKR; cache/scout excluded)",
     "### Example — ETF sleeve lite B (issuer + optional IBKR; cache/social excluded)"),
    ("sherlock/references/confidence-examples.md",
     "BRAIN_REGRADE: B (reason: lite ceiling + <3 chains; cache/scout not A-chains)",
     "BRAIN_REGRADE: B (reason: lite ceiling + <3 chains; cache/social not A-chains)"),
    ("sherlock/references/confidence-examples.md",
     "**Illegal A:** counting `cache/etfs/QQQ.yaml` last-price as a third independent chain.",
     "**Illegal A:** counting a cached quote file as a third independent chain."),
    ("sherlock/references/l2-confidence-contract.md",
     "ETF product / sleeve theses: user-facing grade is still **Brain §1.4**. Issuer factsheet/holdings/ER counts as an independent WEB chain. monorepo `cache/` and Scout heat do **not**.",
     "ETF product / sleeve theses: user-facing grade is still **Brain §1.4**. Issuer factsheet/holdings/ER counts as an independent WEB chain. A research-cache digest (this pack has none) and social heat do **not**."),
    # ---- docs/reference ---------------------------------------------------
    ("docs/reference/methodology-metric-and-bands.md",
     "**性质：** monorepo 研究文档 — **不进入** runtime skill 热路径；",
     "**性质：** engine 方法笔记 — **不进入** runtime skill 热路径；"),
    ("docs/reference/methodology-metric-and-bands.md",
     "**相关：** `plan-valuation-bands-and-methodology.md` · `sources/leiniuniu-*.md` · `skills/finance-master/etf/`  ",
     "**相关：** `../modules/etf/GUIDE.md`  "),
    ("docs/reference/methodology-metric-and-bands.md",
     "金额不在本文件。已有持仓读 `Master/references/data-plane.md`。新买的金额只在主人本轮说出现金数字之后，由 `Master/references/advice.md` 收口。",
     "金额不在本文件。已有持仓读技能入口的数据包契约。新买的金额只在主人本轮说出现金数字之后，由建议卡契约收口。"),
    ("docs/reference/methodology-metric-and-bands.md",
     "| `etf/references/user-capital-policy.md` | 月 cap ~1000；浮动 equity-first |",
     "| `../modules/etf/references/user-capital-policy.md` | 不设月度上限；金额只在主人说出现金数字后写入 |"),
    ("docs/reference/research-bias-checklist.md",
     "权威对照：`methodology-github-borrow-vs-skip.md` §2.2 · `github-borrow-stock-vs-etf-next.md` GH5.",
     "权威对照：本文件即权威；不再引用旧仓路径。"),
    ("docs/reference/research-bias-checklist.md",
     "| Serenity 卡点扫描 | **是**（尤其 leader + English） |",
     "| 卡点/瓶颈扫描 | **是**（尤其 leader + English） |"),
    # ---- etf -------------------------------------------------------------
    ("modules/etf/references/user-capital-policy.md",
     "This pack has no `SESSION_CACHE`. Do not store a capital ceiling. Grouping for this book is `Master/references/book-and-overlaps.md`.",
     "The pack keeps no persistent capital cache; the Brain `SESSION_CACHE` may exist but stores no cash ceiling. Grouping for this book is the skill entry's book-and-overlaps contract."),
    ("modules/etf/GUIDE.md",
     "> **Bands:** do not invent percentiles without a verified series pack (`Master/docs/reference/methodology-metric-and-bands.md`).",
     "> **Bands:** do not invent percentiles without a verified series pack (`../../docs/reference/methodology-metric-and-bands.md`)."),
    # ---- earnings / valuation guides -------------------------------------
    ("modules/earnings-preview/GUIDE.md",
     "- This pack has no research cache. Do not read or write `cache/_template.yaml`. Prior thesis comes only from this turn's pack or Hindsight via `Master/references/memory.md`.",
     "- This pack has no research cache. Do not read or write cache templates. Prior thesis comes only from this turn's pack or Hindsight via the memory contract."),
    ("modules/earnings-recap/GUIDE.md",
     "- This pack has no research cache. Do not read or write `cache/_template.yaml`. Prior pillars come only from this turn's pack or Hindsight via `Master/references/memory.md`. The live print vs estimate is still required.",
     "- This pack has no research cache. Do not read or write cache templates. Prior pillars come only from this turn's pack or Hindsight via the memory contract. The live print vs estimate is still required."),
    ("modules/company-valuation/GUIDE.md",
     "5. Emit `### RETURN_BLOCK`. `Master/references/advice.md` may map `dcf_fair` and `comps_range` onto a target. This skill does not place orders.",
     "5. Emit `### RETURN_BLOCK`. The skill entry's target decision maps `dcf_fair` and `comps_range` onto a target. This skill does not place orders."),
    # ---- deep analysis ---------------------------------------------------
    ("modules/deep-analysis/GUIDE.md",
     "2. **Monorepo research cache:** consume only the Brain `CACHE_HIT|MISS|STALE ticker=…` line already logged this turn (§0.2b). HIT → reuse Brain-injected `one_liner` / `kill` / `open_questions` / `fields_gap`. No Brain log or MISS/STALE → do not claim HIT; do not invent cache. Write-back is Brain §11; suggested fields must match `cache/_template.yaml`.",
     "2. **This pack has no research cache.** Do not claim a cache hit and do not invent cached content. Prior thesis, if any, comes from Hindsight via the memory contract."),
    # ---- finance sentiment ----------------------------------------------
    ("modules/finance-sentiment/GUIDE.md",
     "| X / Twitter | `x_keyword_search` / `x_semantic_search` / `x_thread_fetch` (Grok native) |",
     "| X / Twitter | Bot 内置 X 读取器（关键词 / 语义 / 帖子与线程） |"),
    # ---- serenity --------------------------------------------------------
    ("modules/serenity/GUIDE.md",
     "| **Chain ingest** | Upstream tickers from x-advanced-research / Brain | Score each; prioritize chokepoint-flagged; RETURN Top ≤5 |",
     "| **Chain ingest** | Upstream tickers from the skill entry's discovery run | Score each; prioritize chokepoint-flagged; RETURN Top ≤5 |"),
    ("modules/serenity/GUIDE.md",
     "Brain then: `DATA_PACK.DEEP` + deep-analysis × **≤3**.",
     "Only when the user names deep analysis: the skill entry builds `DATA_PACK.DEEP` and calls deep-analysis × ≤3."),
    ("modules/serenity/GUIDE.md",
     "  next_brain_hint: deep_analysis_top3|stop",
     "  next_brain_hint: stop   # deep-analysis only when the user names it"),
    # ---- ETF research-only wording --------------------------------------
    ("modules/etf/references/product-policy.md",
     "| Single-stock levered | Extra caution; still research-only |",
     "| Single-stock levered | Extra caution; no auto-order; stance only on the advice card |"),
    ("modules/etf/references/modules/m1-taxonomy.md",
     "| `etn_or_complex` | ETN, exotic structures | flag; often avoid or research-only caution |",
     "| `etn_or_complex` | ETN, exotic structures | flag; often avoid or extra caution |"),
    ("modules/etf/references/modules/m6-tactical-levered-long.md",
     "3) If single-stock levered: extra caution block; still research-only; conf ≤ C default",
     "3) If single-stock levered: extra caution block; no auto-order; conf ≤ C default"),
    ("modules/etf/references/modules/m5-income-honesty.md",
     "- Tax regime change → add tax note; still research-only (not tax advice).",
     "- Tax regime change → add tax note; not tax advice; no auto-order."),
]

# ---------------------------------------------------------------------------
# 2. cross-tree path rules (target = skill-root path; made relative per file)
# ---------------------------------------------------------------------------
PATH_RULES = [
    (re.compile(r"Master/docs/reference/([\w.\-]+\.md)"), "references/engine/docs/reference/{1}"),
    (re.compile(r"Master/references/advice\.md"), "references/contracts/advice-card.md"),
    (re.compile(r"Master/references/data-plane\.md"), "references/contracts/data-pack.md"),
    (re.compile(r"Master/references/discovery\.md"), "references/contracts/accounts.md"),
    (re.compile(r"Master/references/memory\.md"), "references/contracts/memory.md"),
    (re.compile(r"Master/references/book-and-overlaps\.md"), "references/contracts/book-and-overlaps.md"),
    (re.compile(r"Master/finance-master/"), "references/engine/"),
    (re.compile(r"(?<![\w/`])etf/references/([\w.\-]+\.md)"), "references/engine/modules/etf/references/{1}"),
]

# ---------------------------------------------------------------------------
# 3. legacy tool names -> capability labels
# ---------------------------------------------------------------------------
TOOL_RULES = [
    ("get_account_positions", "IBKR 持仓读取"),
    ("get_account_balances", "IBKR 账户余额读取"),
    ("get_account_trades", "IBKR 成交读取"),
    ("get_account_orders", "IBKR 委托读取"),
    ("get_price_snapshot", "IBKR 现价快照"),
    ("get_price_history", "IBKR 历史K线"),
    ("search_contracts", "IBKR 合约解析"),
    ("get_option_parameters", "IBKR 期权参数"),
    ("get_option_data", "IBKR 期权链"),
    ("get_company_themes", "IBKR 主题"),
    ("get_company_connections", "IBKR 关联"),
    ("search_futures", "IBKR 期货搜索"),
    ("create_order_instruction", "IBKR 草稿委托(禁止自动调用)"),
    ("delete_order_instruction", "IBKR 删除草稿(禁止自动调用)"),
    ("get_order_instructions", "IBKR 读取草稿(禁止自动调用)"),
    ("x_keyword_search", "X 关键词检索"),
    ("x_semantic_search", "X 语义检索"),
    ("x_thread_fetch", "X 读取帖子/线程"),
    ("x_user_search", "X 用户解析"),
]

# ---------------------------------------------------------------------------
# 4. per-file global cleanups
# ---------------------------------------------------------------------------
GLOBAL_CLEANUPS = {
    "sherlock/references/full-engine.md": [
        ("IBKR|WEB|X|CACHE", "IBKR|WEB|X"),
        ("finance-master/x-advanced-research/", "engine module x-advanced-research: "),
        ("finance-master/serenity-skill/", "engine module serenity: "),
        ("finance-master/etf/", "engine module etf: "),
        ("finance-master/UZI-Skill/", "engine modules UZI: "),
        ("finance-master/finance-skills/", "engine modules finance-skills: "),
    ],
    "sherlock/GUIDE.md": [
        ("finance-master/", ""),
    ],
    "sherlock/references/confidence-examples.md": [("cache/", "research-cache/")],
    "docs/reference/methodology-metric-and-bands.md": [
        ("`docs/archive/labs/etf-valuation-bands/`", "（lab 已不在本包）"),
        ("`docs/archive/labs/etf-valuation-bands/sources.md`", "（lab 已不在本包）"),
        ("`skills/finance-master/etf/**`", "`etf` 模块正文"),
        ("`etf/SKILL.md`", "`etf` GUIDE.md"),
        ("skills/finance-master/etf/", "etf module "),
        ("月 cap ~1000", "金额由主人当轮给出"),
        ("~1000", "由主人当轮给出"),
    ],
    "docs/reference/research-bias-checklist.md": [
        ("Serenity", "卡点/瓶颈"),
        ("monorepo", "pack"),
        ("yfinance", "外部行情源"),
    ],
}


# Applied to every engine text file after the per-file rules.
EXTRA_CLEANUPS: list[tuple[str, str]] = [
    ("monorepo `cache/` digest", "research-cache digest"),
    ("monorepo research cache", "research-cache digest"),
    ("monorepo methodology bands", "engine method bands"),
    ("monorepo research doc", "engine method note"),
    ("monorepo `evals/finance-master/`", "dev evals"),
    ("monorepo `evals/finance-master`", "dev evals"),
    ("monorepo docs", "engine docs"),
    ("monorepo ", "engine "),
    ("monorepo", "engine"),
    ("finance-master/finance-skills/", ""),
    ("finance-master/UZI-Skill/", ""),
    ("finance-master/serenity-skill/", "serenity"),
    ("finance-master/etf/", "etf"),
    ("finance-master/sherlock", "sherlock"),
    ("finance-master/<path>", "<engine module>/GUIDE.md"),
    ("finance-master/", ""),
    ("old monorepo", "old repo"),
    ("详见同目录 `SKILL.md` v4.0", "详见同目录 `GUIDE.md`"),
    ("Hermes MCP 工具链或 Grok web/X search 直接执行", "Bot 的 Web/X 读取器直接执行"),
]


def relpath(target_from_skill: str, current_file: Path) -> str:
    cur_dir = current_file.parent.relative_to(SKILL)
    return _relpath(Path(target_from_skill), cur_dir)


def main() -> int:
    if not ENGINE.is_dir():
        print(f"engine not found: {ENGINE}", file=sys.stderr)
        return 2
    files = [p for p in ENGINE.rglob("*") if p.is_file() and p.suffix in {".md", ".yaml", ".yml"}]
    counts = {"patches": 0, "paths": 0, "tools": 0, "cleanups": 0}
    for f in files:
        relname = str(f.relative_to(ENGINE)).replace("\\", "/")
        text = original = f.read_text(encoding="utf-8")

        for p_rel, old, new in PATCHES:
            if p_rel == relname and old in text:
                text = text.replace(old, new)
                counts["patches"] += 1

        for rx, target in PATH_RULES:
            def _sub(m: re.Match, target=target) -> str:
                tgt = target
                for i, g in enumerate(m.groups(), start=1):
                    tgt = tgt.replace("{" + str(i) + "}", g or "")
                return relpath(tgt, f)
            text, n = rx.subn(_sub, text)
            counts["paths"] += n

        for old, new in TOOL_RULES:
            if old in text:
                counts["tools"] += text.count(old)
                text = text.replace(old, new)

        for old, new in GLOBAL_CLEANUPS.get(relname, []):
            if old in text:
                counts["cleanups"] += text.count(old)
                text = text.replace(old, new)

        for old, new in EXTRA_CLEANUPS:
            if old in text:
                counts["cleanups"] += text.count(old)
                text = text.replace(old, new)

        if text != original:
            f.write_text(text, encoding="utf-8")

    print("counts:", counts)
    leftovers = False
    for f in files:
        t = f.read_text(encoding="utf-8")
        for token in ("Master/", "localhost:8888", "Grok Build", "monorepo", "finance-master/"):
            if token in t:
                print(f"leftover [{token}] {f.relative_to(ENGINE)}")
                leftovers = True
    if not leftovers:
        print("no leftover legacy markers in engine")
    return 0


if __name__ == "__main__":
    sys.exit(main())
