---
name: etf-premium
description: >
  ETF market price vs NAV premium/discount.
  Brain-invoke only (sherlock INVOKE); do not trigger from casual user chat.
  finance-master v4.6.8.
version: 4.6.8
ecosystem: 4.6.8
metadata:
  tags: [finance, us-stocks, etf, nav]
  market_scope: US_EQUITIES_ONLY
  role: L2_TOOL
---

# ETF Premium / Discount · v4.6.8

## Consumer rules

| Field | Source |
|-------|--------|
| Market last / bid-ask | IBKR snapshot / pack |
| NAV / iNAV | Web (issuer, ETF.com, etc.) — often DATA_GAP |
| Holdings / flow narrative | Web |
| Dealer/gamma color | Optional Web; see `references/gamma_squeeze_reference.md` as **concepts only** |

Premium % ≈ (Price − NAV) / NAV × 100. If NAV missing → report price only + DATA_GAP (confidence ≤ B).

**No yfinance `navPrice` requirement.**

## Deliver

- Premium/discount % and $  
- Context: normal band for product type (equity vs bond vs crypto vs levered)  
- Likely drivers: hours mismatch, stress, AP friction (hypothesis-grade)  
- Tradeability note (not arb instructions)

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
skill: etf-premium
status: ok|partial
ticker: SYM
confidence: A|B|C
confidence_scope: single_dim
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [price, nav?]
fields_gap: [...]
artifacts:
  price: ...
  nav: ...|null
  premium_pct: ...|null
  note: "..."
counterfactuals: []
raw_notes: <≤200 words>
```

*v4.6.8 · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only*
