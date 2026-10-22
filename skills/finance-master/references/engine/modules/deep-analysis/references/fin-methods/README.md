# Institutional methods library (v4.6.8 · US live set)

> **Methodology only.** No Python modules.  
> Agent applies formulas in-context using Brain **DATA_PACK** + Web.  
> Market: **US equities only**.

## Live files (load on demand)

| File | Topic | When |
|------|--------|------|
| `ai-readiness.md` | AI exposure / chokepoint readiness | AI theme |
| `serenity-bottleneck.md` | Bottleneck scoring alignment | chain / serenity path |

**Earnings preview:** prefer Brain route to L2 `finance-skills/earnings-preview` — do **not** load legacy fin-methods earnings docs.

## Quarantined (do not load)

Banned / removed from product (`../../../../sherlock/references/banned-patterns.yaml`):

- `task2.5-qualitative-deep-dive.md`  
- `task2-dimension-scoring.md` (old dim numbering)  
- `task3-agent-evaluation.md`  
- `fin-methods/` · `returns-attribution.md` · `model-update.md` · `earnings-preview.md`  

## Core methods (in Brain / main deep pipeline)

| Method | Where |
|--------|--------|
| DCF / Comps / LBO | deep Stage 2 + `task1.5-institutional-modeling.md` |
| IC structure | intent IC memo / D19 |
| Catalyst calendar | D12 + Web |
| US panel | `investor-frameworks.md` |
| Pre-earnings | L2 `earnings-preview` skill |

## Design constraints

1. Formulas over hardcoded prices  
2. Assumptions explicit  
3. Sensitivity for DCF  
4. True data > estimate > default (label each)  
5. Never load quarantine paths  
