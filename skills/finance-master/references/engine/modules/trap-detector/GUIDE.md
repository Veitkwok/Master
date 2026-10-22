---
name: trap-detector
description: >
  Pump-and-dump / tip-trap detector for US equity research (finance-master v4.6.8).
  Trigger when the user mentions friend tips, group/chat gurus, "guaranteed",
  insider rumors, social "hot tips", or explicitly asks if a name is a scam/trap.
  Scans 8 signals via Web + X; market structure from Brain Data Pack or IBKR.
  Returns risk level 🟢🟡🟠🔴 and a RETURN_BLOCK for the Central Brain.
version: 4.6.8
ecosystem: 4.6.8
author: FloatFu-true (original) / Veit Kwok (v4.5 Grok rewrite)
license: MIT
metadata:
  tags: [finance, us-stocks, trap-detection, risk, pump-and-dump]
  market_scope: US_EQUITIES_ONLY
  role: L2_SAFETY
  related_skills:
    - sherlock
    - deep-analysis
---

# Trap Detector · v4.6.8 (US · Brain-invoked)

> **L2 safety skill.** Invoked by `sherlock` §9 / §6 — do **not** self-route to deep-analysis or other L2 skills.  
> Full methodology detail: `references/eight-signals.md`.

---

## Consumer rules (token + integrity)

1. Prefer fields in the Brain **`data_pack`** (quote, volume, 52w move, fundamentals snippets).  
2. **Never** call deleted helpers: `fetch_financials`, `fetch_sentiment`, `fetch_kline`, `fetch_capital_flow`, or any Python `scripts/`.  
3. Market structure (signals 4–5): use Data Pack → else IBKR (`IBKR 合约解析` + `IBKR 现价快照` + optional `IBKR 历史K线`) → else **one** Web price/fundamentals query.  
4. Promotion signals (1–3, 6–8): **Web search + X search** only. Cap ≈ **8–12** new tool calls total.  
5. End with **`### RETURN_BLOCK`** for the Brain. On 🟠/🔴, Brain must **STOP** the research pipeline.

---

## Triggers

| Class | Examples |
|-------|----------|
| Social tip | 朋友推荐、群里说、老师带、跟单、内幕、稳赚、必涨、翻倍 |
| CN platforms | 小红书、抖音、直播间荐股 |
| EN platforms | Discord/Telegram “signals”, “guaranteed runner”, “insider” |
| Explicit | 杀猪盘、是不是套路、pump and dump、safe to buy this tip? |

US tickers only for market structure. Tip language may be Chinese even when the name is US-listed.

---

## 8-signal scan (summary)

| # | Signal | How to gather (v4.6.8) |
|---|--------|----------------------|
| 1 | Coordinated low-quality accounts | Web + X: same ticker + “buy/moon/target” clustering |
| 2 | Template hype language | Phrase search (see reference) |
| 3 | Paid group / VIP funnel | Web: group/VIP/WeChat/Discord invite near ticker |
| 4 | Fundamentals vs hype disconnect | Data Pack / Web financials + X/Web heat — **no fetch_*** |
| 5 | Price already ran into the tip | Data Pack / IBKR history / Web chart summary — **no fetch_kline** |
| 6 | Guru / “teacher” persona | Web + X: “老师/股神/signals coach” + ticker |
| 7 | Cross-platform blast | ≥3 venues (X, Reddit/web, TikTok/web, YouTube, etc.) |
| 8 | Fake research / rumor | Web: “rumor/denied/clarifies” + no sell-side watermark |

Per-signal hit criteria → `references/eight-signals.md`.

---

## User keyword boost

Raise severity by **one full level** (or add +1 to hit count for threshold math) when user text includes:

| Phrases | Boost |
|---------|------:|
| 朋友推荐 / 群里 / 老师带 / friend told me / group chat | +1 |
| 内幕 / 稳赚不赔 / insider / guaranteed | +2 |
| 必涨 / 翻倍 / 暴涨 / “easy 10x” | +1 |

---

## Risk levels

| Hits + boost (effective) | Level | Action for Brain |
|--------------------------|-------|------------------|
| 0–1 | 🟢 安全 | May continue analysis |
| 2–3 | 🟡 注意 | Continue with warnings |
| 4–5 | 🟠 警惕 | **STOP** buy narrative; optional deep only if user insists after warning |
| 6+ | 🔴 高度可疑 | **Hard STOP** research-as-buy path |

If ≥4 hits, user-facing text **must** start with 「强烈建议谨慎」 or 「强烈建议回避」.

---


## L2 confidence (Cog-4 · advisory only)

`confidence` in `### RETURN_BLOCK` is **skill-local deliverable quality**, not user investment confidence.

| Rule | Max grade |
|------|-----------|
| `status: partial` or material `fields_gap` | **B** |
| X/social-only evidence for hard claims | **C** |
| `status: blocked` | no thesis A |
| Complete skill scope + hard sources + no material gaps | **A** allowed (still advisory) |

Default `confidence_scope` for this skill: **safety**.

`confidence` here = quality of the **trap classification**, not “is XYZ a good long.”  
On 🟠/🔴, `hard_stop: true` dominates any buy path regardless of grade letter.

Also emit Cog-4 fields when practical: `confidence_scope`, `confidence_basis` (evidence_independence, physical_mechanical, data_gaps_material), `limiting_factors`.

**Never** emit Brain `### CONFIDENCE_BLOCK` or `mode:` — the Central Brain re-grades via §H.6.

## Output

### User-facing (Markdown)

```markdown
## Trap check · {TICKER|name}

**Level:** 🟢|🟡|🟠|🔴  
**Effective hits:** N (raw hits + keyword boost)

| # | Signal | Status | Evidence |
|---|--------|--------|----------|
| 1 | ... | hit / miss / data_gap | ... |

### Recommendation
...
```

### RETURN_BLOCK (required)

```text
### RETURN_BLOCK
skill: trap-detector
status: ok|partial
ticker: <SYM or UNKNOWN>
confidence: A|B|C
confidence_scope: safety
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
trap_level: green|yellow|orange|red
trap_score: 1-10
fields_filled: [signals_1_8, keyword_boost]
fields_gap: [...]
artifacts:
  signals_hit: [{id, name, severity, evidence}]
  user_keyword_boost: <n>
  recommendation: <one line>
  hard_stop: true|false
counterfactuals: []
raw_notes: <≤200 words>
```

`hard_stop: true` when level is orange or red.

---

## Completion checklist

- [ ] All 8 signals: hit / miss / data_gap  
- [ ] ≥1 concrete URL or post cite unless all green with no promotion found  
- [ ] No `fetch_*` or script calls  
- [ ] RETURN_BLOCK present  
- [ ] Orange/red → explicit stop language for Brain  

---

*v4.6.8 · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only · Brain hard-stop contract*
