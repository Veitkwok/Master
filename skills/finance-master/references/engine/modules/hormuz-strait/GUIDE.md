---
name: hormuz-strait
description: >
  Hormuz / Gulf energy-shipping risk for US-equity macro context.
  Brain-invoke only (sherlock INVOKE); do not trigger from casual user chat.
  finance-master v4.6.8.
version: 4.6.8
ecosystem: 4.6.8
metadata:
  tags: [finance, macro, energy, geopolitics]
  market_scope: MACRO_US_IMPLICATIONS
  role: L2_TOOL
---

# Hormuz Strait · v4.6.8

## Consumer rules

1. Try public monitor: `curl -s https://hormuzstraitmonitor.com/api/dashboard` if network allows; on failure → Web news synthesis.  
2. Web: transit status, insurance war-risk, diplomatic headlines.  
3. Optional IBKR: crude/energy futures snapshot for price context.  
4. Map **implications for US equities** (energy, transports, inflation narrative) — not A-share.  
5. Schema notes: `references/api_schema.md` if dashboard shape needed.

## Deliver

| Section | Content |
|---------|---------|
| Status | Open / impaired / uncertain |
| Shipping & oil | Key stats or qualitative |
| Risk level | Low–extreme (justified) |
| US market transmission | Sectors/tickers sensitive |
| Watch items | Next 48h–2w |

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
skill: hormuz-strait
status: ok|partial
ticker: MACRO
confidence: A|B|C
confidence_scope: single_dim
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [status, risk]
fields_gap: [...]
artifacts:
  status: open|impaired|uncertain
  risk_level: ...
  us_equity_implications: [...]
counterfactuals: []
raw_notes: <≤250 words>
```

*v4.6.8 · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only*
