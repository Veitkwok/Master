# M5 · Income honesty（收益诚实）

**Module id:** `M5`  
**Status:** methodology filled (E-P1 · 2026-08-10)  
**Inputs:** ticker(s) with distributions / “high yield” / monthly pay claims; M1/M2 preferred  
**Outputs:** `income_honesty` block, forced caveats, conf ceiling rules  
**Hard policy:** `../product-policy.md` — violations → rewrite or `blocked`

---

## 1. Purpose

Separate **cash distribution** from **total economic return**.  
Kill “15%+ guaranteed / 稳赚 / safe income + full upside” narratives.

Trigger when user or product involves:

- Covered-call / option-income ETFs (JEPI, JEPQ, QYLD, XYLD, RYLD, …)  
- “Monthly dividend” marketing  
- Distribution rate / SEC yield / 30-day yield as primary pitch  
- Comparing “yield” of QYLD vs SCHD as if same instrument  

---

## 2. Procedure

```text
1) Confirm structure (M1)
   - plain equity dividend index? → dividend honesty lite (still split yield vs TR)
   - options overlay / buy-write / ELN-like? → full M5 template
   - return-of-capital heavy? → flag ROC risk if disclosed

2) Collect facts (issuer + Web; no invented yields)
   - distribution frequency
   - latest distribution rate or trailing yield **as labeled by issuer** (name the label)
   - strategy: call overlay, equity sleeve, bond sleeve if any
   - whether upside is capped / partially sold

3) Mandatory honesty sections (all four for option-income)
   A. Mechanism
   B. Distribution ≠ total return
   C. Bull-market lag / path risk
   D. Role: satellite unless the user explicitly accepts lag. The role feeds ../../../../../contracts/advice-card.md. This module does not choose stance.

4) Forbidden language scan
   - If draft contains 保证/稳赚/必涨/guaranteed 15% → strip; if user demands guarantee framing → status blocked

5) Valuation note
   - Do NOT use distribution rate as 20/50/80 “cheapness” primary (see methodology bands doc)
   - Prefer: price vs NAV (etf-premium), total-return chart narrative, cap structure

6) Emit income_honesty string + structured fields
```

---

## 3. Product subtypes

| Subtype | Examples | Extra emphasis |
|---------|----------|----------------|
| `covered_call_equity` | QYLD, XYLD, JEPI, JEPQ | Cap upside; NAV erosion possible in strong trends |
| `plain_dividend_equity` | SCHD, VYM, DVY | Yield can be legitimate metric_hint with **invert bands**; still not a guarantee; cross with PE |
| `preferred_or_hybrid` | PFF etc. | Rate sensitivity; not equity core |
| `bond_income` | bond ETF distributions | Yield framework ≠ stock PE; duration risk |
| `unknown_income` | unclear | fields_gap; refuse high-certainty yield claims |

---

## 4. Mandatory narrative blocks

### A. Mechanism (1–3 sentences)

What is sold or held to generate cash (e.g. equity book + call overlay).  
If unknown → DATA_GAP, do not invent options strikes.

### B. Distribution vs total return

```text
Required explicit split:
- Distribution rate / yield figure: <value or gap> (label: SEC/trailing/…)
- Total return: price change + distributions − fees; may be << distribution rate in some regimes
- ROC / destructive distribution: mention if issuer discloses material return of capital
```

### C. Bull lag & path

In strong unidirectional bull markets, covered-call strategies often **trail** plain index total return.  
Past high distribution **does not** imply future high total return.

### D. Role & capital

```text
role: satellite (default) | user_accepted_core_substitute (only if user opts in after caveats)
capital_note: no invented ceiling; an income product does not take the whole stated cash figure by default
```

---

## 5. Plain dividend vs covered-call (do not conflate)

| | Plain dividend (SCHD-class) | Covered-call (QYLD/JEPI-class) |
|--|----------------------------|--------------------------------|
| Cash source | Corporate dividends (mostly) | Premiums ± dividends |
| Upside | Full index-ish upside (minus fees) | Often **capped / reduced** |
| DY as cheapness | Possible with invert + PE cross | **Forbidden** as primary cheapness |
| Core sleeve | Possible if user wants dividend core | Default **not** broad total-return core |

---

## 6. Confidence rules (L2 advisory)

| Condition | Max conf |
|-----------|----------|
| Full four blocks + issuer facts | A possible for **honesty explanation** only |
| Yield number without source label | ≤ B; fields_gap |
| Mechanism unknown | ≤ C |
| Any guaranteed-yield language left in draft | **blocked** (fix) |
| User asks “is 12% yield safe income?” without accepting caveats | ≤ C + strong caveats; no buy framing |

Honesty module **never** alone justifies buy narrative; Brain §6/§10 if user forces buy question.

---

## 7. Artifact shape (M5)

```text
artifacts.income_honesty_struct:
  SYM:
    subtype: covered_call_equity|plain_dividend_equity|...
    distribution_label: "trailing 12m yield"|SEC|...
    distribution_value: number|null
    total_return_note: "..."
    mechanism: "..."
    upside_cap: true|false|unknown
    roc_risk: true|false|unknown
    role: satellite|user_accepted_core_substitute
    forbidden_language_cleared: true
    fields_gap: []

artifacts.income_honesty: |
  <compressed 80–160 words covering A–D>
```

Parent RETURN_BLOCK must set:

```text
artifacts.income_honesty: <non-null when M5 ran>
confidence: respect ceilings above
```

---

## 8. Mini templates

### Covered-call (fill blanks)

```text
Mechanism: holds [equity sleeve]; generates cash partly via [call overlay / buy-write].
Distribution figure [X%] is a [label], not a guaranteed income rate and not equal to total return.
In strong bull regimes this structure often lags uncapped index total return because upside is [sold/capped].
Research role: satellite unless you explicitly accept lag vs core β. Floating capital envelope applies; not a fixed income annuity.
```

### Plain dividend

```text
Cash mainly from constituent dividends; yield [X%] ([label]) can inform relative cheapness only with history and PE cross-check — not a promise.
Total return still includes price drawdowns. Not immune to dividend cuts or sector shocks.
```

---

## 9. Counterfactuals

- Overlay removed / strategy change → re-run M1/M5.  
- User accepts “I want cash and accept lag” → role may become `user_accepted_core_substitute` with explicit note.  
- Tax regime change → add tax note; not tax advice; no auto-order.

---

## 10. Linkage

| Doc | Use |
|-----|-----|
| `../product-policy.md` | Hard forbids |
| engine method bands | No DY percentile as cheapness for covered-call |
| M2 | `needs_m5` flag |
| M6 | levered is separate; do not mix with income honesty |

---

*M5 · E-P1 · no yield guarantees · no live order · stance is ../../../../../contracts/advice-card.md*
