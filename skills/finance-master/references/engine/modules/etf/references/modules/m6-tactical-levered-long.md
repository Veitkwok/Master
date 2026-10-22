# M6 · Tactical levered long（战术杠杆多头）

**Module id:** `M6`  
**Status:** methodology filled (E-P3 · 2026-08-10)  
**Inputs:** levered-long ticker (e.g. TQQQ, UPRO, SOXL) or user “levered long” ask; M1 required  
**Outputs:** `levered_plan` caveats, horizon box, size framework, `roles=tactical`, conf ceilings  
**Hard policy:** `../product-policy.md` — inverse is **not** this module (refuse investment path)

---

## 1. Purpose

Research framing for **US levered long ETFs** only: short-horizon expression of beta, with daily-reset / path-dependency honesty.  
**Not** core. **Not** “hold forever.” **Not** inverse/short products.

---

## 2. Gate checks (run first)

```text
1) M1 class must be levered_long (or reclass if 2x/3x daily objective confirmed).
2) If inverse / short:
     → do NOT run M6 as investable plan
     → taxonomy-only + roles=avoid; inverse_requested=true
3) If single-stock levered: extra caution block; no auto-order; conf ≤ C default
4) User wants “core” or “long-term DCA into TQQQ”:
     → refuse core assignment; rewrite to tactical-only or status partial with hard no
5) Valuation 10y PE bands: valuation_band_eligible=false (M1); do not invent p20/p50/p80
```

---

## 3. Mandatory education blocks (all must appear)

### A. Daily reset / target leverage

Issuer targets a **daily** multiple of an index (e.g. +3x Nasdaq-100).  
Holding multi-day, the path of returns ≠ simple 3× index cumulative return.

### B. Path dependency / volatility decay

Choppy sideways markets can **erode** NAV vs a naive leveraged buy-and-hold story even if the index ends flat-to-up.  
This is structural, not a temporary “glitch.”

### C. Horizon box

| Horizon | Research stance |
|---------|-----------------|
| Intraday – few days | Only range where daily target is designed to approximate |
| Weeks | Possible but path risk rises; require explicit thesis + kill |
| Months–years as core | **Out of policy** for this product skill |

Default research language: **days to a small number of weeks**, with calendar or thesis kill.

### D. Not a substitute for unlevered core

Core β (VOO/QQQ-class) remains the long-horizon sleeve (M4).  
Levered long = optional **tactical** overlay on remaining envelope only.

---

## 4. Procedure

```text
1) M1 (+ optional M2 card: ER, liquidity).
2) Emit education A–D (short, clinical).
3) Thesis requirement:
   - User/Brain must state catalyst or technical window in ≤3 bullets
   - If none → conf ≤ C; prefer “no tactical sleeve” rather than invent thesis
4) Size framework (no live order; stance is ../../../../../contracts/advice-card.md):
   - Soft cap: ≤ 10% of the ETF sleeve (M4), and only inside cash the user stated this turn
   - Prefer notional such that a −20% to −40% product move is survivable
   - Never put all stated cash into TQQQ
5) Kill / exit research conditions (examples):
   - Thesis invalid (catalyst failed)
   - Horizon box expired
   - Volatility regime exploded vs entry assumption
   - User switched to long-term hold narrative → force reclass discussion
6) Brain may add sepa/trend or IBKR structure; M6 does not replace §12/§13
7) artifacts.levered_long_tactical = true; roles[SYM]=tactical
```

---

## 5. Interaction matrix

| Module / skill | Role |
|----------------|------|
| M1 | class + reset_horizon=daily |
| M2 | ER, ADV sketch |
| M4 | tactical sleeve band 0–10% |
| M5 | N/A unless product also income (rare) |
| M7 | May gate “add tactical?” vs wait — if regime hostile, prefer wait |
| sepa-strategy | Brain-optional trend template; not auto-entry |
| stock-liquidity | Large notional on levered names |
| Inverse products | **Out** — product-policy |

---

## 6. Confidence (L2 advisory)

| Condition | Ceiling |
|-----------|---------|
| Clear daily-reset education + horizon + kill + no core claim | B typical |
| “Hold TQQQ for years as core” user demand | **C** + rewrite; or blocked if guarantee language |
| No thesis / no kill | ≤ C |
| Single-stock 2x/3x | ≤ C |
| Guaranteed profit / 稳赚 | **blocked** |
| Taxonomy-only inverse explanation | ok with avoid role; not M6 invest plan |

Default: **never A** for levered long **buy** framing without Brain full conf stack and physical pack — even then Brain re-grades.

---

## 7. Artifact shape (M6)

```text
artifacts.levered_plan:
  SYM:
    reset: daily
    target_multiple: "3x"| "2x"| unknown
    horizon_box: "days–weeks"
    education:
      daily_reset: true
      path_dependency: true
      not_core: true
    thesis_bullets: []
    kill_conditions: []
    size_framework: "≤10% ETF sub-book; fraction of remaining envelope"
    valuation_bands: "not_applicable"
fields_gap: []  # e.g. target_multiple unknown

artifacts.roles: { SYM: tactical }
artifacts.levered_long_tactical: true
artifacts.modules_run: [..., M6]
```

`raw_notes` ≤400 words clinical; no emoji cheerleading.

---

## 8. Forbidden language

| Forbidden | Replace with |
|-----------|----------------|
| “Safe leveraged upside” | Path-dependent; can lose faster than index |
| “Hold through the cycle” | Policy: not core; horizon box |
| “Same as 3× QQQ forever” | False for multi-day paths |
| Inverse as hedge “plan” here | Out of scope investment path |

---

## 9. Counterfactuals

- Issuer changes objective / non-daily → re-run M1.  
- User accepts only unlevered → empty tactical sleeve.  
- Horizon exceeded without kill → research exit framing, not “average more.”

---

*M6 · E-P3 · tactical only · no inverse path · no live order · stance is ../../../../../contracts/advice-card.md*
