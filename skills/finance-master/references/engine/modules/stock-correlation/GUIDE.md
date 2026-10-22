---
name: stock-correlation
description: >
  Realized correlation / co-movement among US tickers.
  Brain-invoke only (sherlock INVOKE); do not trigger from casual user chat.
  finance-master v4.6.8.
version: 4.6.8
ecosystem: 4.6.8
metadata:
  tags: [finance, us-stocks, correlation]
  market_scope: US_EQUITIES_ONLY
  role: L2_TOOL
---

# Stock Correlation · v4.6.8

## Consumer rules

1. Resolve each ticker (IBKR `IBKR 合约解析`).  
2. `IBKR 历史K线` daily, aligned window (default 6m–1y).  
3. Compute pairwise Pearson on log returns (agent-side).  
4. If single ticker: use IBKR themes/peers or `references/sector_universes.md` ideas + Web to pick candidates, then correlate.  
5. Budget: prefer ≤8 names in one matrix.  
6. No yfinance.


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

## Output

- Correlation matrix (table)  
- Highest / lowest pairs  
- Note: correlation ≠ causation; regime-dependent  
- Optional: rolling comment if two windows compared  

```text
### RETURN_BLOCK
skill: stock-correlation
status: ok|partial
ticker: SYM|MULTI
confidence: A|B|C
confidence_scope: single_dim
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [matrix]
fields_gap: [...]
artifacts:
  window: ...
  pairs_top: [{a,b,rho}]
  pairs_low: [{a,b,rho}]
counterfactuals: []
raw_notes: <≤250 words>
```

*v4.6.8 · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only*
