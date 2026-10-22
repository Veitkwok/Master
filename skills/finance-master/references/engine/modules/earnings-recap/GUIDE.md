---
name: earnings-recap
description: >
  Post-earnings recap for US stocks: beat/miss, reaction, guidance, takeaways.
  v4.6.8: Web + X + IBKR price reaction; no yfinance required.
  Structured skeleton (B-P1d): beat/miss table, guidance triad, thesis pillar S/U/W, no ratings.
  Triggers: earnings recap, did they beat, post-earnings, surprise, how did earnings go.
version: 4.6.8
ecosystem: 4.6.8
metadata:
  tags: [finance, us-stocks, earnings, recap]
  market_scope: US_EQUITIES_ONLY
  role: L2_TOOL
---

# Earnings Recap · v4.6.8

> Post-print **what’s new**, not an initiation report and not a rating change product.  
> The skeleton in this file is the template. `anthropic-er-vs-earnings-diff.md` is not in this pack.

## Consumer rules

- **Web:** actual EPS/rev vs estimate, guidance, call highlights, segment color.  
- **IBKR:** spot vs prior close / session move; optional history around print.  
- **X (optional):** immediate narrative — Tier C; not sole physical proof.  
- This pack has no research cache. Do not read or write cache templates. Prior pillars come only from this turn's pack or Hindsight via the memory contract. The live print vs estimate is still required.  
- No yfinance install path. Cap tool calls tightly.  
- Do not emit Maintain/Raise/Lower, a street price target, or “buy/sell the open” as an order. Beat/miss, guidance, and pillar impact feed `../../../contracts/advice-card.md`. This skill does not choose stance.  
- Brain owns the grade (§1.4 / §H.6) and then the advice card.

### Freshness gate (mandatory · recency bias)

```text
1) Write today's date.
2) Confirm you have the *latest* release for the quarter discussed (release date within a sensible window of the event).
3) Prefer earnings release + 10-Q/8-K + transcript when available; cite with dates.
4) Training-memory quarters without a live source check → partial / re-fetch.
```

---

## Deliver skeleton (user-facing order)

**Lead with quantified beat/miss.** Numbers before adjectives.

### 1. Beat / miss table (lead)

| Metric | Reported | Est / consensus | Variance | Source asof |
|--------|----------|-----------------|----------|-------------|
| Revenue | | | $ / % | |
| EPS (adj vs GAAP — label which) | | | | |
| Key KPI (if material) | | | | |

Headline one-liner: beat / in-line / miss + **why** (driver), not just “strong.”

### 2. Price reaction (IBKR)

- Spot vs prior close / session % if known.  
- Optional: vs recent range.  
- If outside RTH and session empty → use history bars; label clearly.

### 3. Guidance triad

| Item | New guidance | Prior guidance | Street (if known) | Take |
|------|--------------|----------------|-------------------|------|
| Revenue / EPS / other | | | | raised / maintained / lowered / none |

If no formal guide: say so; use qualitative outlook from call with source.

### 4. Thesis pillars impact (if prior thesis exists)

Only when pack, deep context, SESSION_CACHE, or GH2 thesis supplies pillars. Else one line: `No prior thesis on file.`

| Pillar (short) | Impact | Evidence from print |
|----------------|--------|---------------------|
| … | STRENGTHENED \| UNCHANGED \| WEAKENED | 1–2 numbers |

Do not invent broker fills. Do not open `docs/archive/`.

### 5. Three takeaways + three open questions

- Takeaways: concrete, numeric where possible.  
- Open questions: what next print / KPI / guide must answer.

### 6. Street revision direction (light)

- Up / down / flat / unknown for NTM EPS or revenue narrative.  
- Deep revision work → Brain may INVOKE `estimate-analysis`; this skill only needs a one-liner if data is thin.

### 7. RETURN_BLOCK

Always end with L2 block below.

---

## Deliver (compact checklist)

1. Beat/miss table (Reported \| Est \| Var) — **lead**  
2. Stock reaction (IBKR)  
3. Guidance: new vs prior vs street  
4. Thesis pillars S/U/W (or “no prior thesis”)  
5. Three takeaways + three open questions  
6. Street revision direction (one line)  
7. RETURN_BLOCK — no sell-side rating; stance stays on the advice card

---

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

```text
### RETURN_BLOCK
skill: earnings-recap
status: ok|partial
ticker: SYM
confidence: A|B|C
confidence_scope: single_dim
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [actuals, reaction, guidance?, pillars?, takeaways]
fields_gap: [...]
artifacts:
  eps_actual_vs_est: ...
  rev_actual_vs_est: ...
  price_reaction_pct: ...
  guidance_triad: {new, prior, street, direction}
  pillar_impacts: [{pillar, impact: STRENGTHENED|UNCHANGED|WEAKENED|null}]
  takeaways: [...]
  open_questions: [...]
  revision_bias: up|down|flat|unknown
counterfactuals: []
raw_notes: <≤250 words>
```

*v4.6.8 · B-P1d skeleton · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only*
