# Method Library INDEX (Cog-3 · first 12)

**Authority:** Central Brain `../../GUIDE.md` §M owns **when** to load.  
**Never** load this entire folder into context. Load **only** cards listed by §M for the current turn.

**Data plane (all cards):** IBKR MCP → Web → X. **Banned:** yfinance, longbridge, funda, AkShare, opencli readers.

## Mode gates (summary)

| mode_effective | Max cards / turn | Default |
|----------------|-----------------:|---------|
| **lite** | **0** | Off (clinical language already in §8.L) |
| **standard** | **0–3** | Only if trigger keywords match |
| **max** | **1–6** (cap 6 even if more match) | Intent-ranked from table below |

Token control: if tool budget nearly exhausted, **skip cards** and note `method_cards: skipped_budget` in SESSION_CACHE.

## Card registry

| ID | File | Title | Primary triggers (any) | Prefer mode |
|----|------|-------|------------------------|-------------|
| M01 | `think/M01-obs-before-deduce.md` | Observation before deduction | premature thesis, “first impression”, headline reaction | std/max |
| M02 | `think/M02-reverse-reconstruction.md` | Reverse reconstruction | fragmented clues, “add it up”, hidden timeline, footnote oddities | max; std forensic |
| M03 | `think/M03-asymmetry.md` | Asymmetry / symmetry-break | pattern break, peer decouple, disclosure inconsistency | std/max |
| M04 | `think/M04-brain-attic.md` | Brain Attic curation | info overload, noisy feeds, what to ignore | std/max |
| M05 | `think/M05-physical-priority.md` | Physical / mechanical priority | FCF vs EPS, inventory, DSO, Form 4, tape vs story | std/max |
| M06 | `think/M06-anti-conspiracy.md` | Anti-conspiracy baseline | fraud narrative, collusion claim, “everyone is in on it” | max; std if fraud |
| M07 | `think/M07-empty-space.md` | Empty space as evidence | missing disclosure, no buyback, silence where expected | max; std forensic |
| M08 | `think/M08-rest-test.md` | Rest Test / energy consistency | story too smooth, incentives vs effort, “does this rest?” | max |
| M09 | `judge/M09-role-behavior.md` | Role–behavior consistency | management “strategy” vs capex/buybacks/comp | std/max |
| M10 | `judge/M10-provocation-stress.md` | Provocation / scenario stress | guidance credibility, margin claims, what-if attacks | std/max |
| M11 | `speak/M11-clinical-compression.md` | Clinical compression (deep) | long report, fluff risk, max write-up | max (std optional) |
| M12 | `limits/M12-empathy-pollution.md` | Empathy / narrative pollution | story stock, charismatic CEO, crowd euphoria | all if B2; else max |

## Selection algorithm (Brain)

```
1. mode_effective == lite → load none
2. Collect cards whose triggers match user intent OR path (forensic/earnings/fraud/chain)
3. Rank: M05, M01, M03, M02, M09, M07, M10, M06, M08, M04, M12, M11
4. Truncate to mode max (std 3, max 6)
5. Emit METHOD_CARDS_LOADED: [ids]
6. Apply card ops inside §1 Steps 2–5; do not replace §D/§9
```

## Invocation phrase (internal)

```text
LOAD method-library/<path>  # only paths from this INDEX
```
