---
name: sepa-strategy
description: >
  Mark Minervini SEPA / trend template / VCP / Stage-2 for US stocks.
  Brain-invoke only (sherlock INVOKE); do not trigger from casual user chat.
  finance-master v4.6.8.
version: 4.6.8
ecosystem: 4.6.8
metadata:
  tags: [finance, us-stocks, sepa, technical, minervini]
  market_scope: US_EQUITIES_ONLY
  role: L2_TOOL
---

# SEPA Strategy · v4.6.8

## Consumer rules

1. **Price/MAs/volume:** pack `ohlcv.daily` or IBKR `IBKR 历史K线` (`ONE_DAY`, ≥1y preferred).  
2. **52w high/low, spot:** IBKR snapshot or pack.  
3. **EPS/sales growth:** Web (not yfinance skill).  
4. Load detail refs only as needed: `references/trend-template.md`, `stage-analysis.md`, `patterns.md`, `entry-rules.md`, `position-sizing.md`, `fundamentals.md`, `market-environment.md`.

## Checklist (pass/fail)

| Gate | Criterion (classic SEPA) |
|------|---------------------------|
| Trend template | Price > 50 > 150 > 200 MA; 200 MA rising; within ~25% of 52w high; ≥30% above 52w low (standard rules — state if modified) |
| Stage | Stage 2 preferred |
| Fundamentals | EPS/sales acceleration if data exists |
| Setup | VCP / base / pivot defined |
| Risk | Stop below pivot/structure; R-multiple stated |

Output: each gate ✅/❌ + setup quality A/B/C + invalidation level. Not a broker order.

```text

## L2 confidence (Cog-4 · advisory only)

`confidence` in `### RETURN_BLOCK` is **skill-local deliverable quality**, not user investment confidence.

| Rule | Max grade |
|------|-----------|
| `status: partial` or material `fields_gap` | **B** |
| X/social-only evidence for hard claims | **C** |
| `status: blocked` | no thesis A |
| Complete skill scope + hard sources + no material gaps | **A** allowed (still advisory) |

Default `confidence_scope` for this skill: **single_dim**.

Also emit Cog-4 fields when practical: `confidence_scope`, `confidence_basis` (evidence_independence, physical_mechanical, data_gaps_material), `limiting_factors`.

**Never** emit Brain `### CONFIDENCE_BLOCK` or `mode:` — the Central Brain re-grades via §H.6.

### RETURN_BLOCK
skill: sepa-strategy
status: ok|partial
ticker: SYM
confidence: A|B|C
confidence_scope: single_dim
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [trend_template, stage, setup?]
fields_gap: [...]
artifacts:
  trend_template_pass: true|false
  stage: 1|2|3|4|unknown
  pivot: <num|null>
  stop: <num|null>
  setup_grade: A|B|C
counterfactuals: [{signal, window}]
raw_notes: <≤300 words>
```

*v4.6.8 · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only*
