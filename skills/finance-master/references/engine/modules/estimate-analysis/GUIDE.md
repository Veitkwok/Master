---
name: estimate-analysis
description: >
  Analyst estimate levels, revisions, and growth trajectory.
  Brain-invoke only (sherlock INVOKE); do not trigger from casual user chat.
  finance-master v4.6.8.
version: 4.6.8
ecosystem: 4.6.8
metadata:
  tags: [finance, us-stocks, estimates, revisions]
  market_scope: US_EQUITIES_ONLY
  role: L2_TOOL
---

# Estimate Analysis · v4.6.8

## Consumer rules

- Web: current Q/FY EPS & rev estimates, # analysts, revision direction (up/down last 30–90d), long-term growth if published.  
- Pack/IBKR: price to contextualize multiple compression.  
- DATA_GAP rather than invent consensus.  
- No yfinance/funda required.

## Analysis frame

| Lens | Question |
|------|----------|
| Level | Where is street now? |
| Momentum | Revisions up or down? |
| Dispersion | Tight or wide (if available)? |
| Growth bridge | NTM vs LT growth story |
| Price | Spot vs implied if targets exist |

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
skill: estimate-analysis
status: ok|partial
ticker: SYM
confidence: A|B|C
confidence_scope: single_dim
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [consensus, revisions?]
fields_gap: [...]
artifacts:
  eps_fwd: ...
  rev_fwd: ...
  revision_bias: up|down|flat|unknown
  one_liner: "..."
counterfactuals: []
raw_notes: <≤250 words>
```

*v4.6.8 · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only*
