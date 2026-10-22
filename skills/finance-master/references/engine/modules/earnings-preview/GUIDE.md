---
name: earnings-preview
description: >
  Pre-earnings briefing for US stocks: date, consensus, beat/miss history, setup.
  v4.6.8: Brain DATA_PACK + Web/X; IBKR for price reaction context. No yfinance required.
  Structured skeleton (B-P1d): street table, sector ops KPIs, bull/base/bear, catalyst checklist.
  Triggers: earnings preview, what to expect, consensus estimates, before earnings, whisper.
version: 4.6.8
ecosystem: 4.6.8
metadata:
  tags: [finance, us-stocks, earnings, preview]
  market_scope: US_EQUITIES_ONLY
  role: L2_TOOL
---

# Earnings Preview · v4.6.8

> Pre-print **setup**, not a rating or order.  
> The skeleton in this file is the template. `anthropic-er-vs-earnings-diff.md` is not in this pack.

## Consumer rules

- Pack quote + `options_summary` if present (IV crush / implied-move context).  
- **Web:** earnings date, EPS/rev consensus, prior beat rate, guidance snippets, sector KPIs.  
- **X (optional):** street narrative / whisper tone — **Tier C**; never sole A-grade support.  
- IBKR snapshot for spot + short-term perf into the print.  
- This pack has no research cache. Do not read or write cache templates. Prior thesis comes only from this turn's pack or Hindsight via the memory contract.  
- No yfinance/funda/longbridge. Cap ~6–8 tool calls.  
- Do not invent a sell-side rating or a street price target. Do not write “buy the print” as an order. This skill reports the setup. `company-valuation` supplies `dcf_fair` and `comps_range` when a target is required. Stance is only `../../../contracts/advice-card.md`.

### Freshness gate (mandatory · recency bias)

```text
1) Write today's date (asof research day).
2) Search for the *next* or *relevant* earnings materials — do not invent from training cut-off.
3) Every consensus number needs asof (or DATA_GAP).
4) If materials are stale / wrong quarter → status partial or re-search; never present old quarter as current.
```

---

## Deliver skeleton (user-facing order)

Use this order. Mark missing rows `DATA_GAP` — do not invent.

### 1. When + consensus asof

| Field | Content |
|-------|---------|
| Company / ticker | US listing |
| Quarter | e.g. Q2 FY26 (fiscal calendar if non-calendar) |
| Earnings date / time | BMO / AMC / unknown |
| Consensus asof | date of estimate snapshot |

### 2. Street table

| Metric | Consensus | YoY / notes | Source asof |
|--------|-----------|-------------|-------------|
| Revenue | | | |
| EPS (adj if stated) | | | |
| Key segment / KPI (if material) | | | |

### 3. Sector ops watchlist (3–5 KPIs)

Pick **sector-relevant** operating metrics the print must clear (examples, not all required):

| Sector cue | Example KPIs |
|------------|----------------|
| Tech / SaaS | ARR, NRR, RPO, customers |
| Retail | SSS, traffic, basket |
| Industrials | Backlog, book-to-bill, price/volume |
| Financials | NIM, credit, loans, fees |
| Healthcare | Scripts, volumes, pipeline |

Rank by importance to **this** name’s narrative.

### 4. Bull \| Base \| Bear

| Scenario | Revenue / EPS idea | Key driver | Qualitative price frame |
|----------|-------------------|------------|-------------------------|
| Bull | | | |
| Base | | | |
| Bear | | | |

For each: what ops print + what management tone would signal it. Historical reaction only if sourced.

### 5. Catalyst checklist (ranked 3–5)

```text
1. [Metric] vs consensus/whisper — why it moves the stock
2. [Guidance item] — what buy-side needs to hear
3. [Narrative / strategic] — mix, M&A, restructuring, etc.
```

### 6. Setup + risks

- Spot (IBKR) + path into print; IV / implied move if pack has options.  
- History: last 4–8 quarters beat/miss **if available**.  
- Risks: what breaks the setup (guidance cut, KPI miss, multiple compression).  
- Whisper: optional; label Tier C / unconfirmed.

### 7. RETURN_BLOCK

Always end with L2 block below.

---

## Deliver (compact checklist)

| Block | Content |
|-------|---------|
| When | Next report date / BMO/AMC + consensus asof |
| Street | EPS & rev (+ segment if known) table |
| Ops KPIs | 3–5 sector-specific watch items |
| Scenarios | Bull / base / bear table |
| Catalysts | Ranked 3–5 |
| Setup | Price into print, IV if known, beat history |
| Risks | What breaks the setup |

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
skill: earnings-preview
status: ok|partial
ticker: SYM
confidence: A|B|C
confidence_scope: single_dim
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [date, consensus, ops_kpis?, scenarios, catalysts, setup?]
fields_gap: [...]
artifacts:
  earnings_date: ...
  consensus_asof: ...
  eps_consensus: ...
  rev_consensus: ...
  ops_watchlist: [...]
  scenarios: {bull, base, bear}
  catalyst_checklist: [...]
  setup_one_liner: "..."
  implied_move_note: null|"..."
counterfactuals: []
raw_notes: <≤250 words>
```

No separate API reference file. Use Brain **DATA_PACK** + **Web** (dates/consensus) + optional **X**; IBKR for spot/reaction only. Do not load yfinance/funda paths.

*v4.6.8 · B-P1d skeleton · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only*
