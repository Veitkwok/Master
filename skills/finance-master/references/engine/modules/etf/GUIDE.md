---
name: etf
description: >
  Top-level US ETF research & plan skill for finance-master (v0.4.0).
  Full M1–M7 methodology: taxonomy, product card, compare, core-satellite,
  income honesty, tactical levered long, opportunity window. NOT guaranteed
  yields. Invoked by Sherlock. Inverse out of scope. IBKR + Web/issuer only.
version: 0.4.0
ecosystem: 4.6.8
author: Veit Kwok
license: MIT
metadata:
  tags: [finance, us-stocks, etf, portfolio, core-satellite, research]
  market_scope: US_EQUITIES_ONLY
  role: L2_ETF_PLAN
  status: METHODS_COMPLETE
  related_skills:
    - sherlock
    - etf-premium
    - stock-liquidity
    - sepa-strategy
---

# ETF · Plan & Research (v0.4.0)

> **Status: E-P1–E-P3 methods complete** — M1–M7 filled; eval (E-P4) optional next.  
> **L2 under `sherlock`.** Do not self-route to other L2 except Brain may also INVOKE `etf-premium` / liquidity for entry checks.  
> **No live submit.** No “guaranteed return”. Sleeve gates (`add_etf`, `wait`, `prefer_stocks`, `trim_satellite`, `no_new_risk`) feed `../../../contracts/advice-card.md`. This skill does not write a second buy card and does not place an order.  
> **This book’s grouping** is `../../../contracts/book-and-overlaps.md`. Product method stays M1–M7.  
> **Bands:** do not invent percentiles without a verified series pack (`../../docs/reference/methodology-metric-and-bands.md`).

Load on demand:

| File | Role |
|------|------|
| `references/architecture.md` | Module map + Brain handoff |
| `references/product-policy.md` | Hard product redlines |
| `references/user-capital-policy.md` | Owner capital envelope (floating monthly) |
| `references/modules/README.md` | Module index + load matrix |
| `references/modules/m1-taxonomy.md` | **M1** classification |
| `references/modules/m2-product-card.md` | **M2** single-product card |
| `references/modules/m3-compare.md` | **M3** multi-ETF compare |
| `references/modules/m4-core-satellite.md` | **M4** sleeve / capital framework |
| `references/modules/m5-income-honesty.md` | **M5** distribution vs total return |
| `references/modules/m6-tactical-levered-long.md` | **M6** levered long tactical |
| `references/modules/m7-opportunity-window.md` | **M7** opportunity / regime gate |

---

## Consumer rules

1. Prefer Brain **DATA_PACK** for market structure (IBKR). Prefer **`pack.issuer`** for ER, NAV, holdings asof, index/strategy.  
2. **Web / issuer** only for keys **missing** from the pack (NAV, holdings, expense ratio, distribution policy) — and only if `budget.may_fetch: true`. Omitted or `false` = do not re-fetch present keys; missing issuer keys → `fields_gap`. Never yfinance/funda/opencli.  
3. If the pack has no ticker list, work on **roles** (core / satellite / tactical) and name the gap. Watchlists Favorites, ETFs, Assets, Nasdaq-QQQ, and Candidate come from `../../../contracts/data-pack.md`. Do not invent symbols that are not in the pack or the user message.  
4. Do not invent a monthly cash ceiling. Size a new buy only after `../../../contracts/advice-card.md`, and only if the user states a cash figure. The historical table in `references/user-capital-policy.md` does not apply to the existing book.  
5. Cap tool calls ~8–16 for single-product; multi-compare ~12–20 under max mode.  
6. End with **`### RETURN_BLOCK`** for Brain. Never emit Brain `### CONFIDENCE_BLOCK`. Stance is only `../../../contracts/advice-card.md`.  
7. This pack has no research cache. Follow sherlock §0.2b: `CACHE_MISS`. Do not read or write `cache/_template.yaml`.

---

## Intent → module (routing contract)

| User intent | Module id | Notes |
|-------------|-----------|--------|
| What kind of ETF is this? | **M1 taxonomy** | Broad / sector / bond / equal-weight / covered-call / levered long… |
| Compare / pick among ETFs | **M2 product-card + M3 compare** | Fees, holdings, overlap, role |
| Is this for long-term core? | **M4 core-satellite** | Core β vs satellite |
| High yield / monthly pay | **M5 income-honesty** | Distribution ≠ total return; no 15% guarantee |
| TQQQ / short levered long | **M6 tactical-levered-long** | Short horizon only; never inverse |
| Buy the dip / opportunity day | **M7 opportunity-window** | Regime gates feed `../../../contracts/advice-card.md` |
| Premium/discount now | **→ etf-premium** (adjacent L2) | Brain may INVOKE separately |
| Liquidity / spread | **→ stock-liquidity** | Adjacent |

---

## Hard product policy (summary)

| Rule | Binding |
|------|---------|
| No “guaranteed 15%+” / 稳赚 / 必涨 framing | **Always** |
| Inverse / short ETFs (e.g. SQQQ, SPXU) | **Out of scope** — refuse as investment path |
| Levered **long** (e.g. TQQQ) | **Tactical short-horizon only**; not long-term core |
| Covered-call / high distribution ETFs | Allowed as **satellite research**; always show total-return risk |
| Fixed ticker universe | **Not required**; user-supplied or open research |
| Monthly budget | Do not invent a ceiling. See `references/user-capital-policy.md` |

Full text: `references/product-policy.md`, `references/user-capital-policy.md`.

---

## Deliver

**Implemented (E-P1 + E-P2 + E-P3):**

- **M1** role_hint + class + valuation_band_eligible + metric_hint  
- **M2** product card fields + fields_gap  
- **M3** compare table + overlap_proxy + pick_framework  
- **M4** sleeve_map + rebalance/capital frameworks (floating envelope)  
- **M5** income_honesty when yield/covered-call/monthly pay  
- **M6** levered long tactical plan (daily reset, horizon box, not core)  
- **M7** opportunity gate: add_etf / wait / prefer_stocks / trim_satellite / no_new_risk  

Always: counterfactuals. M7 gates and sleeve roles feed `../../../contracts/advice-card.md`. No live order. No guaranteed yield. Mention cash only when the user stated a figure.  
Never invent p20/p50/p80 without series pack (`bands: unavailable`).

### Module load cheat-sheet

| Intent | Modules |
|--------|---------|
| What kind / role | M1 |
| Fees, holdings, product facts | M1 + M2 |
| High yield / JEPI / QYLD / monthly pay | M1 + M2 + **M5** |
| Compare 2+ ETFs | M1 + M2 + **M3** |
| Core vs satellite / how to sleeve | M1 (+M2/M3) + **M4** |
| TQQQ / levered long | M1 + M2 + **M6** (+ **M7** if timing) |
| Buy the dip / add ETF now? | M1 (+M4) + **M7** (+ M5/M6 by product) |

---

## L2 confidence (Cog-4 · advisory only)

| Rule | Max grade |
|------|-----------|
| `status: partial` or material `fields_gap` | **B** |
| Income/levered claims without total-return / path caveats | **C** |
| Guaranteed-yield or “must bounce” language | **blocked** (fix narrative) |
| Invented valuation percentiles | **blocked** / rewrite |
| Levered long framed as multi-year core | **C** + rewrite (M6) |
| Complete scope + hard sources (non-levered) | **A** allowed (still advisory) |

Default `confidence_scope`: **single_dim** (plan/product).  
Plan multi-name screens: pre-deep style ceiling **≤ B** until packs close.

### RETURN_BLOCK (contract)

```text
### RETURN_BLOCK
skill: etf
status: ok|partial|blocked
ticker: SYM|MULTI
confidence: A|B|C
confidence_scope: single_dim
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [modules_run, roles?, cards?]
fields_gap: [...]
artifacts:
  modules_run: [M1, ...]
  roles: { SYM: core|satellite|tactical|avoid }
  inverse_requested: false
  levered_long_tactical: true|false
  capital_note: "no invented ceiling; size only if the user stated cash"
  income_honesty: "..." | null
  opportunity_window: "..." | null
  compare_summary: {...} | null
  sleeve_map: {...} | null
  levered_plan: {...} | null
  opportunity_window_struct: {...} | null
counterfactuals: []
raw_notes: <≤400 words>
```

---

## Implementation checklist

- [x] E-P1: M1 + M2 + M5 methodology  
- [x] E-P2: M3 + M4 methodology  
- [x] E-P3: M6 + M7 methodology  
- [x] E-P4: eval GP07/GP08 + NEG11/NEG12 under dev evals  
- [ ] Optional: user watchlist file under engine docs (not runtime required)  

---

*etf v0.4.0 · M1–M7 · ecosystem 4.6.8 · top-level L2 · no inverse · no yield guarantees · no live order · stance is ../../../contracts/advice-card.md*
