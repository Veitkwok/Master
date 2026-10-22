# M3 · Compare / screen（多品对比）

**Module id:** `M3`  
**Status:** methodology filled (E-P2 · 2026-08-10)  
**Inputs:** 2–N tickers (user list); prefer prior M1 (+ M2 cards) per name  
**Outputs:** compare table, `overlap_proxy`, `pick_framework` (not a hard “winner trade”), `fields_gap[]`  
**Hard policy:** `../product-policy.md` · capital: `../user-capital-policy.md`

---

## 1. Purpose

Answer: **How do these ETFs differ on cost, structure, role, and rough overlap — and what would change a research pick?**  
Not a broker recommendation. Not automatic portfolio weights (that is M4).

---

## 2. Preconditions

```text
1) N tickers ≥ 2 (if N=1 → M1/M2 only).
2) Cap N: standard ≤ 6; max mode ≤ 10. Over cap → ask user to prioritize or batch.
3) For each SYM: run M1 (required). M2 preferred; if thin card → fields_gap per name.
4) Any inverse in set: may appear in table as taxonomy, but cannot win investment pick;
   set roles[SYM]=avoid for path planning.
5) Any income_option: if user compares on “yield”, force M5 notes on those rows.
6) Any levered_long: flag tactical-only; do not rank as core.
```

Tool budget: multi-compare ~12–20 under max; prefer pack reuse; do not re-fetch packed keys.

---

## 3. Procedure

```text
1) Build row set from M1/M2 for each ticker.
2) Align columns (canonical table below); mark null as DATA_GAP not zero.
3) Overlap / redundancy:
   - Same index or near-identical exposure (e.g. SPY vs VOO vs IVV) → high overlap_proxy
   - Same sector different issuer → high-med
   - Broad vs sector → complementary note, not “duplicate”
   - Do not claim holdings-overlap % without data; use qualitative proxy only
4) Score framework (research labels, not trade ranks):
   - cost_edge: lower ER among same-class peers
   - structure_fit: matches user stated goal (core β / income / sector bet)
   - complexity_penalty: leverage, options overlay, ETN, young listing
   - liquidity_note: ADV/spread from pack if available
5) Emit pick_framework:
   - If same class: “prefer lower ER + adequate liquidity + clearer index”
   - If different class: “not substitutes; use M4 for sleeve roles”
   - Never: “buy X sell Y tomorrow”
6) Floating capital one-liner if user asks how much into winner
```

---

## 4. Canonical compare table

| Column | Source | Notes |
|--------|--------|--------|
| `ticker` | user | |
| `class` | M1 | |
| `role_hint` | M1/M2 | core / satellite / tactical / avoid |
| `expense_ratio` | M2 / issuer | null if gap |
| `aum_usd` | M2 | optional |
| `index_or_strategy` | M2 | short string |
| `distribution_note` | M2 | or “n/a” |
| `reset_horizon` | M1 | daily / none |
| `metric_hint` | M1 | for later bands; not live pXX |
| `quote_last` | IBKR pack | optional |
| `liquidity_sketch` | pack ADV/spread | optional |
| `overlap_proxy` | M3 logic | low / med / high / unknown |
| `complexity` | M3 | low / med / high |
| `fields_gap` | list | per row |

Markdown table in `raw_notes` or `artifacts.compare_table` as list-of-dicts.

---

## 5. Overlap proxy rules (qualitative)

| Situation | `overlap_proxy` |
|-----------|-----------------|
| Same primary index (S&P 500 trackers) | **high** |
| Same sector classification, similar top holdings narrative | **high** or **med** |
| Broad market vs single sector | **low** (complementary) |
| Equity broad vs bond | **low** |
| Equity vs covered-call on same underlying family | **med** (related risk, different payoff) |
| Insufficient holdings data | **unknown** + fields_gap |

**Do not** invent correlation numbers; Brain may INVOKE `stock-correlation` separately for price co-move (not holdings overlap).

---

## 6. Pick framework templates

### Same-exposure race (e.g. VOO vs SPY vs IVV)

```text
Same economic exposure class. Research pick drivers: (1) expense ratio,
(2) liquidity for user’s size, (3) structural quirks (unit size, commission-free
at user’s broker — user-stated only). Tracking difference often small vs fee gap.
Not a timing call.
```

### Sector vs broad

```text
Not substitutes. Broad = core β candidate; sector = satellite concentration.
M4 for sleeve weights; M3 only clarifies fee/structure within each bucket.
```

### Income vs total-return core

```text
Yield figure is not the selection score. Run M5 on income names. Prefer
uncapped core for long-horizon total return unless user accepts lag.
```

### Includes levered / inverse

```text
Levered rows: tactical only; exclude from core race.
Inverse rows: no investment path; table educational only.
```

---

## 7. Confidence (L2 advisory)

| Condition | Ceiling |
|-----------|---------|
| All rows have class + ER + clear same/different class | A possible for **compare structure** |
| Multi-name plan sold as single ranking without gaps | ≤ B |
| Material ER/holdings gaps on key names | ≤ B, `partial` |
| Screen of many names with thin cards | ≤ B (pre-deep style) |
| Guarantee language in pick | blocked rewrite |

Default multi-name screens: conf scope `single_dim`, ceiling **≤ B** until packs dense.

---

## 8. Artifact shape (M3)

```text
artifacts.compare_table:
  - ticker: VOO
    class: equity_broad
    role_hint: core
    expense_ratio: 0.0003
    ...
    overlap_proxy: high
    complexity: low
    fields_gap: []
  - ticker: ...

artifacts.compare_summary:
  same_exposure_group: true|false
  pick_framework: "..."
  preferred_research_focus: [SYM, ...]   # soft; not order list
  excluded_from_core: [levered/inverse/...]
  capital_note: "floating envelope..."

artifacts.modules_run: [..., M3]
fields_filled: [..., compare_table]
```

Parent `ticker: MULTI` when N>1.

---

## 9. Counterfactuals

- Fee cut on lagging peer → re-rank cost_edge.  
- User changes goal from “income” to “total return” → re-weight framework, re-run M5 emphasis.  
- Liquidity event → prefer higher ADV row for larger notional frameworks.

---

*M3 · E-P2 · no live order · no auto-orders · stance is ../../../../../contracts/advice-card.md*
