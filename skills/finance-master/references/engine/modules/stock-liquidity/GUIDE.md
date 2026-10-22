---
name: stock-liquidity
description: >
  US equity liquidity: spreads, volume, ADV USD, rough impact. v4.6.8 uses Brain pack /
  IBKR snapshot fields (bid_ask, volume, avg_90d_usd_volume). No yfinance required.
  Triggers: liquidity, bid-ask, ADV, can I size, market impact, hard to trade.
version: 4.6.8
ecosystem: 4.6.8
metadata:
  tags: [finance, us-stocks, liquidity]
  market_scope: US_EQUITIES_ONLY
  role: L2_TOOL
---

# Stock Liquidity · v4.6.8

## Consumer rules

| Metric | Source |
|--------|--------|
| bid, ask, last, volume | IBKR `IBKR 现价快照` / pack |
| avg_90d_usd_volume | IBKR snapshot field |
| 52w context | `misc_statistics` |
| Historical volume profile | IBKR `IBKR 历史K线` if needed |

**Banned required path:** yfinance. Full-order-book L2 not available — say so.

## Analysis

1. Quoted spread $ and % of mid  
2. ADV USD vs intended notionals (if user gave size)  
3. Days to trade X% ADV heuristic  
4. Grade: **High / Medium / Low / Micro** liquidity  
5. Caution for wide spread + low ADV  

Detail ideas: `references/liquidity_reference.md` (IBKR / DATA_PACK field map; methodology only).

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
skill: stock-liquidity
status: ok|partial
ticker: SYM
confidence: A|B|C
confidence_scope: single_dim
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [spread, adv]
fields_gap: [...]
artifacts:
  mid: ...
  spread_pct: ...
  avg_90d_usd_volume: ...
  liquidity_grade: high|medium|low|micro
  impact_note: "..."
counterfactuals: []
raw_notes: <≤200 words>
```

*v4.6.8 · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only*
