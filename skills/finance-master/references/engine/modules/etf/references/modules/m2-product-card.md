# M2 · Product card（单品卡）

**Module id:** `M2`  
**Status:** methodology filled (E-P1 · 2026-08-10)  
**Inputs:** ticker; Brain DATA_PACK preferred; Web/issuer; optional prior M1  
**Outputs:** product card fields, `fields_gap[]`, optional `role_hint` refine  
**Adjacent:** Brain may also run `etf-premium`, `stock-liquidity` — this module does not call them.

---

## 1. Purpose

Build a **single-ETF research card**: fees, structure, holdings snapshot, distribution policy, liquidity sketch inputs.  
Framework language only — no “buy N shares.”

---

## 2. Procedure

```text
1) Run or reuse M1 taxonomy (class, flags, role_hint).

2) Market structure (IBKR / DATA_PACK)
   - last, bid/ask if any, volume, ADV if present, 52w context
   - outside RTH: follow Sherlock outside-RTH rule (history bars, not invent OHLC)
   - Do not treat empty session volume as “illiquid forever”

3) Product facts (Web / issuer / prospectus / factsheet)
   - expense ratio (net)
   - AUM if published
   - inception / listing age (years)
   - index name + methodology one-liner OR active/strategy description
   - top holdings (top 5–10) + top sector if available
   - distribution frequency + latest distribution policy note
   - replication: physical / sampling / synthetic if stated

4) Quality checks
   - ER missing → fields_gap; do not invent
   - Holdings stale (>1 quarter without date) → flag asof_gap
   - Covered-call / high dist → set needs_m5=true

5) Role refine (optional)
   - Very high ER vs peers for same exposure → bias away from core
   - Extremely concentrated top-10 → satellite caution
   - Do not place an order. Role and card fields feed ../../../../../contracts/advice-card.md.

6) Emit card + gaps + capital_note reminder (floating envelope)
```

---

## 3. Card fields (canonical)

| Field | Type | Source priority | Required for `ok` |
|-------|------|-----------------|:-----------------:|
| `ticker` | str | user / pack | ✅ |
| `name` | str | issuer / IBKR | ✅ |
| `class` | enum | M1 | ✅ |
| `expense_ratio` | number\|null | issuer | prefer |
| `aum_usd` | number\|null | issuer/Web | optional |
| `inception_or_years` | str\|null | issuer | optional |
| `index_or_strategy` | str\|null | issuer | prefer |
| `top_holdings` | list\|null | issuer/Web | optional |
| `sector_tilt` | str\|null | Web | optional |
| `distribution_frequency` | str\|null | issuer | if income product |
| `distribution_note` | str\|null | issuer | if income product |
| `replication` | str\|null | issuer | optional |
| `quote_last` | number\|null | IBKR | prefer |
| `asof_market` | str\|null | IBKR | prefer |
| `asof_fundamentals` | str\|null | Web | optional |
| `liquidity_sketch` | str\|null | ADV/spread from pack | optional |
| `needs_m5` | bool | M1/M2 logic | ✅ |
| `needs_m6` | bool | levered long | ✅ |
| `role_hint` | enum | M1 refined | ✅ |
| `metric_hint` | str\|null | M1 method table | optional |
| `fields_gap` | list | always compute | ✅ |

**Banned fillers:** yfinance, funda, opencli readers, fabricated AUM/ER.

---

## 4. Data plane rules

| Need | Do | Don't |
|------|-----|--------|
| Price / ADV | IBKR pack | Yahoo as primary when IBKR up |
| ER / holdings | Issuer PDF/HTML, SEC N-CSR/N-PORT summaries via reputable Web | Guess from memory |
| NAV premium | Leave to `etf-premium` unless Brain already packed it | Treat discount as alpha |
| Personal holdings | User paste only | IBKR account tools |

If core card fields missing → `status: partial`, conf ≤ B.

---

## 5. Field completeness tiers

| Tier | Condition | status | conf ceiling |
|------|-----------|--------|--------------|
| Full | name + class + ER + quote + index/strategy | ok | A allowed (taxonomy+card only) |
| Working | name + class + quote; ER or holdings gap | partial | ≤ B |
| Thin | class only / no quote / wrong listing | partial | ≤ C |
| Blocked path | inverse investment plan requested | blocked or taxonomy-only ok | — |

---

## 6. Peer context (light — full compare is M3)

When useful, one line:

```text
peer_note: "Same exposure family as VOO/IVV; compare ER and tracking in M3 if user asks pick."
```

Do not run full multi-ticker table unless user intent is compare → M3 (not yet filled: say framework-only or list fields to compare).

---

## 7. Capital envelope hook

Always attach soft language when sizing comes up:

```text
capital_note: "No invented monthly ceiling. Size only if the user stated a cash figure this turn. Do not apply a historical $600–$1000 table to the existing book."
```

Never deploy the whole stated cash figure into one ETF on a named date.

---

## 8. Artifact shape (M2)

```text
artifacts.product_card:
  SYM:
    name: ...
    class: ...
    expense_ratio: 0.0003
    aum_usd: null
    inception_or_years: "..."
    index_or_strategy: "..."
    top_holdings: []
    sector_tilt: null
    distribution_frequency: null
    distribution_note: null
    replication: null
    quote_last: ...
    asof_market: ...
    asof_fundamentals: null
    liquidity_sketch: "ADV ..."
    needs_m5: false
    needs_m6: false
    role_hint: core
    metric_hint: pe_forward
    peer_note: null
    fields_gap: []
```

Parent RETURN_BLOCK:

```text
fields_filled: [modules_run, roles, cards]
artifacts.modules_run: [M1, M2]
artifacts.roles: { SYM: core|satellite|tactical|avoid }
```

---

## 9. Worked micro-examples (illustrative field fill)

### Broad core (VOO-class)

- class: `equity_broad`, role_hint: `core`, needs_m5/m6: false  
- metric_hint: `pe_ttm` or `pe_forward`  
- Emphasize ER + diversification; not distribution rate  

### Covered-call (JEPI-class)

- class: `income_option`, role_hint: `satellite`, needs_m5: **true**  
- metric_hint: `none` for DY-percentile cheapness  
- Card must not treat SEC yield as total return  

### Levered long (TQQQ-class)

- class: `levered_long`, role_hint: `tactical`, needs_m6: **true**  
- metric_hint: none for 10y bands  
- Holding-period warning in raw_notes  

---

## 10. Counterfactuals

- ER revised after fee cut → may upgrade toward core.  
- Index methodology change (mega-cap concentration) → revisit metric_hint / satellite vs core.  
- Liquidity collapse (ADV crash) → Brain should pull stock-liquidity; role may shift avoid for size.

---

*M2 · E-P1 · no live order · stance is ../../../../../contracts/advice-card.md*
