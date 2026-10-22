# M1 · Taxonomy（分类）

**Module id:** `M1`  
**Status:** methodology filled (E-P1 · 2026-08-10)  
**Inputs:** ticker and/or plain-language product description  
**Outputs:** `class`, `structure_flags`, `reset_horizon`, `role_hint`, `valuation_band_eligible`, `fields_gap[]`  
**Hard policy:** `../product-policy.md` overrides this file on conflict.

---

## 1. Purpose

Answer: **What kind of product is this, and which sleeves / modules are legal?**  
Do not price, do not size, do not say “buy.”

---

## 2. Procedure

```text
1) Resolve identity
   - Prefer Brain DATA_PACK / IBKR contract (US listing).
   - Web/issuer: full name, issuer, index or strategy description.
   - If ticker unknown → ask or stop with fields_gap.

2) Classify structure (order matters — first hard hit wins path)
   - Inverse / short daily? → investment path OUT; taxonomy-only + refuse sleeve plan
   - Levered long (2x/3x daily)? → class=levered_long; role_hint=tactical; M6 only for plan
   - Covered-call / option-income / high distribution strategy? → flag income_strategy; M5 required if yield discussed
   - Bond / rate / credit ETF? → class=bond_*; valuation stock bands N/A
   - Commodity / precious metal / pure futures roll? → class=commodity_*; stock PE bands N/A
   - Equity index product? → continue to equity subtype

3) Equity subtype
   - Broad market (S&P 500, total market, developed, …)
   - Style (growth/value/quality/dividend broad)
   - Sector / industry
   - Factor / smart-beta (equal-weight, low-vol, momentum, …)
   - Thematic (narrow narrative)
   - International / country (still US-listed wrapper)

4) Emit role_hint (soft; M4 may revise)
   - core: low-cost broad equity β for long horizon
   - satellite: sector/factor/theme/dividend/income
   - tactical: levered long only; short horizon
   - avoid: inverse investment path; or product outside US research scope

5) valuation_band_eligible (for future M7 / lab — not live bands unless pack has series)
   - true: unlevered equity broad/sector/factor with stable or mappable metric tree
   - false: inverse, levered, covered-call primary, bond, commodity, very young index without history note
```

---

## 3. Class vocabulary (canonical)

| `class` | Examples (not exhaustive) | `role_hint` default |
|---------|---------------------------|---------------------|
| `equity_broad` | SPY, VOO, IVV, VTI, ITOT | core |
| `equity_style` | VUG, VTV, QUAL | core or satellite |
| `equity_dividend` | SCHD, VYM, DVY | satellite (sometimes core if user wants income sleeve) |
| `equity_sector` | XLK, XLF, SMH, SOXX, KBE | satellite |
| `equity_thematic` | narrow theme ETFs | satellite |
| `equity_factor` | RSP, MTUM, USMV | satellite |
| `equity_intl` | VXUS, EFA, EEM (US-listed) | satellite / diversifier |
| `bond_agg` | BND, AGG | satellite / ballast (not stock core) |
| `bond_duration` | TLT, IEF, SHY | satellite / macro |
| `commodity` | GLD, SLV, USO | satellite / macro; no stock PE bands |
| `income_option` | JEPI, JEPQ, QYLD, XYLD | satellite; **M5** |
| `levered_long` | TQQQ, UPRO, SOXL | **tactical only** |
| `inverse` | SQQQ, SPXU, SPXS | **avoid** as investment path |
| `etn_or_complex` | ETN, exotic structures | flag; often avoid or extra caution |
| `unknown` | insufficient data | fields_gap; no firm role |

Multiple flags allowed in `structure_flags[]`:  
`daily_reset`, `options_overlay`, `physical_replication`, `synthetic`, `high_turnover_index`, `young_listing`.

---

## 4. `reset_horizon`

| Value | When |
|-------|------|
| `none` | Ordinary index / bond / commodity fund |
| `daily` | Stated daily leverage or inverse objective |
| `monthly_or_other` | Non-daily target (rare; document issuer language) |
| `unknown` | Leverage suspected but not confirmed |

Daily reset → path dependency / volatility decay must appear in raw_notes if user asks about holding period (detail in M6 when planning).

---

## 5. Valuation-band eligibility (link to engine method)

Research method (not auto numbers): `../../../../docs/reference/methodology-metric-and-bands.md`.

| Class | Band system | Primary metric **hint** (hypothesis until series exist) |
|-------|-------------|--------------------------------------------------------|
| equity_broad / style | stock percentile OK | PE TTM or forward; QQQ → PE not PB |
| equity_sector cyclical (semi, banks, energy) | stock percentile OK | PB or cycle-adj PE |
| equity_dividend (plain) | stock percentile OK | DY invert + PE cross |
| income_option | **not** DY-as-cheap | total return / cap / premium — M5 |
| levered_long / inverse | **no** 10y band plan | M6 / refuse |
| bond_* | yield/spread framework | not equity PE |
| commodity | macro | not equity PE |

Runtime must **not** invent p20/p50/p80 without a verified series pack. Emit `metric_hint` + `valuation_band_eligible` only.

---

## 6. Inverse path (mandatory language)

If `class=inverse`:

```text
status may stay ok for taxonomy-only explanation.
artifacts.roles[SYM] = avoid  (for investment planning)
artifacts.inverse_requested = true
raw_notes: "Taxonomy only. Product policy: no inverse investment sleeve."
```

Do not build DCA, core weight, or opportunity-window **buy** framing for inverse.

---

## 7. Artifact shape (M1)

```text
artifacts.taxonomy:
  SYM:
    class: equity_broad|...
    structure_flags: []
    reset_horizon: none|daily|...
    role_hint: core|satellite|tactical|avoid
    valuation_band_eligible: true|false
    metric_hint: pe_forward|pe_ttm|pb|dy_invert|none|yield_framework
    issuer: string|null
    index_or_strategy: string|null
```

---

## 8. Confidence local notes

| Situation | L2 conf ceiling (advisory) |
|-----------|----------------------------|
| Clear issuer docs + known product family | A possible for taxonomy alone |
| Ambiguous leverage / options overlay | ≤ B; fields_gap |
| Ticker unresolved | partial / C |

---

## 9. Counterfactuals (examples)

- If product is actually daily 3x → reclass to `levered_long`, role tactical.  
- If “dividend” is covered-call → reclass `income_option`, force M5.  
- If US-listed but non-US primary research ask → Brain §4 US-only gate.

---

*M1 · E-P1 · no live order · stance is ../../../../../contracts/advice-card.md*
