---
name: startup-analysis
description: >
  Three-lens startup analysis (VC / job applicant / founder).
  Brain-invoke only (sherlock INVOKE); do not trigger from casual user chat.
  finance-master v4.6.8.
version: 4.6.8
ecosystem: 4.6.8
metadata:
  tags: [finance, startup, vc, career]
  market_scope: US_PRIMARY
  role: L2_TOOL
---

# Startup Analysis · v4.6.8

## Consumer rules

- Web-only research (company site, news, funding databases via search).  
- **Do not** call quarantined `yc-reader` / opencli-reader.  
- If public US ticker exists, optional IBKR quote.  
- Frameworks: `references/vc-framework.md`, `job-applicant-framework.md`, `ceo-framework.md`.

## Three lenses (default all)

| Lens | Core questions |
|------|----------------|
| VC | Market, product, traction, team, defensibility, round terms |
| Job applicant | Runway, equity realism, growth, culture signals, role leverage |
| Founder/CEO | PMF, burn efficiency, org health, competitive pressure |

End with: aligned insights vs tensions across lenses. Research support only.

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
skill: startup-analysis
status: ok|partial
ticker: NAME|SYM
confidence: A|B|C
confidence_scope: single_dim
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [vc, job, founder]
fields_gap: [...]
artifacts:
  vc_verdict: ...
  job_verdict: ...
  founder_health: ...
  top_risks: [...]
counterfactuals: []
raw_notes: <≤350 words>
```

*v4.6.8 · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only*
