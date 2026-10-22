---
name: serenity-skill
description: >
  Supply-chain bottleneck hunter (theme scans, ticker scorecards).
  Brain-invoke only (sherlock INVOKE); do not trigger from casual user chat.
  finance-master v4.6.8.
version: 4.6.8
ecosystem: 4.6.8
license: MIT
metadata:
  tags: [finance, us-stocks, serenity, bottleneck, supply-chain]
  market_scope: US_EQUITIES_DEFAULT
  role: L2_ORCHESTRATOR_BOTTLENECK
  author: muxu-compatible community build / Veit Kwok (v4.5 finance-master)
  related_skills:
    - sherlock
---

# Serenity.skill · v4.6.8 (US-default · Brain handoff)

Turn the agent into a **supply-chain bottleneck hunter** (public Serenity / @aleabitoreddit-inspired method).

> **L2 under `sherlock`.** Accept Brain INVOKE + optional upstream tickers from `x-advanced-research`.  
> **Do not** call `deep-analysis` or `x-advanced-research` yourself. Emit `### RETURN_BLOCK` and stop.

Research support only — no trade execution.

---

## Core promise

```text
market story → system change → required parts → chain layers → scarce constraints
  → public companies → evidence → what market may miss → what falsifies the idea
```

Plain-language partner tone. Lead with scarce **layers**, then companies.

---

## Consumer rules (finance-master)

1. **Default market = US** listed equities / US-relevant suppliers.  
2. Non-US names only if user explicitly asks multi-market **and** Brain allows; still prefer US liquid names for deep follow-on.  
3. If `data_pack` / upstream `tickers[]` present → **do not rebuild universe from scratch** unless empty.  
4. Scoring: `references/bottleneck-scoring.md` (agent-applied, no scripts).  
5. Evidence: Web + filings; X is lead-gen only (`references/evidence-ladder.md`).  
6. Prices: Brain pack or IBKR if budget allows — not required for pure chain ranking.  
7. Token: chain mode score **≤15** upstream names → return **Top ≤5** scored; standalone theme scan aim 20 candidates → Top 3–7.  
8. **Never** lateral-INVOKE deep-analysis (Brain does Top ≤3 next).

---

## Modes

| Mode | When | Behavior |
|------|------|----------|
| **Chain ingest** | Upstream tickers from the skill entry's discovery run | Score each; prioritize chokepoint-flagged; RETURN Top ≤5 |
| **Theme scan** | Theme only (AI power, HBM, CPO, etc.) | Full workflow; US company list |
| **Single-name challenge** | One ticker | Position in chain + evidence + fail conditions |
| **Compare** | Several tickers | Rank by scarcity proximity + evidence |
| **Dialogue / learn** | Method chat | One sharp question per turn; see dialogue protocol |

---

## Research workflow (theme / ranking)

1. **Scope** — market (default US), theme, 3–12m window  
2. **System change** — what strains the old design?  
3. **Map chain** — demand → integrators → modules → chips → process/pack → equipment → materials → infrastructure  
4. **Scarce layers** — low supplier count, long qual, hard capex, purity, certification, lead times  
5. **Universe** — ≥20 when deep scan allowed; else label “initial pass”  
6. **Evidence** — primary > trade press > social leads; target ≥25 sources on full scans when tools allow  
7. **Rank** — 8-factor score (`bottleneck-scoring.md`); separate layer rank vs company rank  
8. **Falsifiers** — substitution, expansion, demand miss, dilution, geo  
9. **Next checks** — concrete filings/metrics  

---

## Chain handoff protocols

### Input (from Brain / x-advanced-research)

```text
tickers: [{symbol, catalyst_or_bottleneck, x_evidence, risk_flags}]
theme: optional
budget: max_new_tool_calls, may_fetch
```

### Output (to Brain — not to deep-analysis directly)

For each kept name:

```text
symbol, scarce_layer, chain_position, bottleneck_score 0-100,
evidence[2+], evidence_strength, main_risk, falsifier,
why_rank
```

Only when the user names deep analysis: the skill entry builds `DATA_PACK.DEEP` and calls deep-analysis × ≤3.

---

## Evidence & style

- Every top name: “what does it constrain?” + ≥2 evidence points + strength + main fail mode  
- Open theme answers with **layers first**  
- User language; Chinese when user writes Chinese  
- Avoid: guaranteed returns, buy/sell commands, invented contracts  

US source paths preferred: SEC, transcripts, IR, 8-K/10-Q — see `references/market-source-playbook.md` (**US section first**; A/HK = non-default).

---

## Communication snippets

EN: `Start with the layers: [L1], [L2], [L3]. Then who controls the hard-to-scale parts.`  
ZH: `先排产业链层级，再排公司。优先：[层级1/2/3]。`

Company row: `constrains / sits at / why ranked / evidence / main risk`

---

## RETURN_BLOCK (required)

```text

## L2 confidence (Cog-4 · advisory only)

`confidence` in `### RETURN_BLOCK` is **skill-local deliverable quality**, not user investment confidence.

| Rule | Max grade |
|------|-----------|
| `status: partial` or material `fields_gap` | **B** |
| X/social-only evidence for hard claims | **C** |
| `status: blocked` | no thesis A |
| Complete skill scope + hard sources + no material gaps | **A** allowed (still advisory) |

Default `confidence_scope` for this skill: **discovery**.

Grade = quality of **bottleneck scorecards**, not final deep thesis. Brain pre-deep ranking **≤ B**; `recommended_for_deep` ≤3.

Also emit Cog-4 fields when practical: `confidence_scope`, `confidence_basis` (evidence_independence, physical_mechanical, data_gaps_material), `limiting_factors`.

**Never** emit Brain `### CONFIDENCE_BLOCK` or `mode:` — the Central Brain re-grades via §H.6.

### RETURN_BLOCK
skill: serenity-skill
status: ok|partial
ticker: MULTI|SYM
confidence: A|B|C
confidence_scope: discovery
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [layers, scorecards]
fields_gap: [...]
artifacts:
  mode: chain_ingest|theme_scan|single|compare|dialogue
  scarce_layers_ranked: [..]
  scored_tickers:
    - symbol: XXX
      us_listed: true
      bottleneck_score: 0-100
      scarce_layer: "..."
      chain_position: "..."
      evidence: [...]
      evidence_strength: strong|medium|weak|lead
      main_risk: "..."
      falsifier: "..."
  recommended_for_deep: [XXX, YYY, ZZZ]   # max 3
  next_brain_hint: stop   # deep-analysis only when the user names it
counterfactuals: [...]
raw_notes: <≤400 words>
```

`recommended_for_deep` length **≤3**.

---

## Load-on-demand refs

| File | When |
|------|------|
| `references/bottleneck-scoring.md` | Scoring |
| `references/deep-research-workflow.md` | Full theme scans |
| `references/evidence-ladder.md` | Source grade |
| `references/market-source-playbook.md` | Filings paths (US first) |
| `references/serenity-dialogue-protocol.md` | Dialogue mode |
| `references/output-style-and-language.md` | Tone |
| `references/risk-and-compliance.md` | Boundaries |
| `references/evidence-ladder.md` | **Primary demo shape (US/global infra)** |
| A-share demo examples | **Removed from product** — US-first only |

---

*v4.6.8 · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only*
