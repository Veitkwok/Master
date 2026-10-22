---
name: company-valuation
description: >
  US equity intrinsic value via DCF, peer multiples, and SOTP when applicable.
  finance-master v4.6.8: consume Brain DATA_PACK / IBKR→Web — no yfinance requirement.
  Triggers: DCF, fair value, intrinsic, undervalued, peer valuation, SOTP, WACC, price target from fundamentals.
version: 4.6.8
ecosystem: 4.6.8
metadata:
  tags: [finance, us-stocks, valuation, dcf, comps, sotp]
  market_scope: US_EQUITIES_ONLY
  role: L2_TOOL
---

# Company Valuation · v4.6.8 (US)

> **L2 tool.** Invoked by `sherlock`. Prefer Brain **data_pack**; gap-fill IBKR (price/peers) + Web (statements).  
> **Banned as required path:** yfinance install loops, funda skill, longbridge.

## Consumer rules

1. Use pack quote / fundamentals / peers first.  
2. Spot price: IBKR `IBKR 合约解析` → `IBKR 现价快照` (or pack).  
3. Financials / shares / segments: Web filings or pack.  
4. Peers: IBKR themes/connections or pack; else Web.  
5. Emit `### RETURN_BLOCK`. The skill entry's target decision maps `dcf_fair` and `comps_range` onto a target. This skill does not place orders.  
6. US listings only.

## Methods (default: run all that apply)

| Method | When | Output |
|--------|------|--------|
| **DCF** | Positive / modelable FCF | FV/sh + 5×5 sensitivity (WACC × g) |
| **Relative** | ≥3 peers | Implied price from PE / EV/Sales / EV/EBITDA medians |
| **SOTP** | ≥2 distinct segments with data | Sum of segment values − net debt |

US defaults (override with note): rf ≈ 10Y UST, ERP 4.5–5.5%, tax ~21%+state, terminal g 2–2.5%. Detail: `references/dcf.md`, `relative_valuation.md`, `sotp.md`, `wacc_erp_rates.md` (adapt any A-share leftovers to US).

## Workflow

1. Resolve ticker + spot + shares diluted  
2. Build FCFF path (5y) or mark DCF weak  
3. Peer table + implied range  
4. SOTP if segments available (else skip)  
5. Triangulate: show disagreement; optional blend with weights explained  
6. Bull/Base/Bear one-liners  


## L2 confidence (Cog-4 · advisory only)

`confidence` in `### RETURN_BLOCK` is **skill-local deliverable quality**, not user investment confidence.

| Rule | Max grade |
|------|-----------|
| `status: partial` or material `fields_gap` | **B** |
| X/social-only evidence for hard claims | **C** |
| `status: blocked` | no thesis A |
| Complete skill scope + hard sources + no material gaps | **A** allowed (still advisory) |

Default `confidence_scope` for this skill: **valuation**.

Also emit Cog-4 fields when practical: `confidence_scope`, `confidence_basis` (evidence_independence, physical_mechanical, data_gaps_material), `limiting_factors`.

**Never** emit Brain `### CONFIDENCE_BLOCK` or `mode:` — the Central Brain re-grades via §H.6.

## Output

Markdown: assumptions, DCF, comps table, SOTP (if any), sensitivity, vs spot upside/downside, confidence A/B/C.

```text
### RETURN_BLOCK
skill: company-valuation
status: ok|partial|blocked
ticker: SYM
confidence: A|B|C
confidence_scope: valuation
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [dcf, comps, sotp?]
fields_gap: [...]
artifacts:
  spot: <num>
  dcf_fair: <num|null>
  comps_range: [lo, hi]|null
  sotp_fair: <num|null>
  blended_note: "..."
counterfactuals: []
raw_notes: <≤300 words>
```

*v4.6.8 · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only*
