# M4 · Core–satellite（核心–卫星）

**Module id:** `M4`  
**Status:** methodology filled (E-P2 · 2026-08-10)  
**Inputs:** user goals / risk language; optional tickers; M1 roles; optional M3 table; capital policy  
**Outputs:** `sleeve_map`, `rebalance_framework`, `capital_split_framework`, `roles{}`, `fields_gap[]`  
**Hard policy:** product-policy + user-capital-policy  

---

## 1. Purpose

Answer: **How might sleeves be organized (core β / satellite / tactical / avoid) under a floating monthly envelope — as a research framework, not an order ticket?**

---

## 2. Sleeve definitions

| Sleeve | Intent | Typical classes (M1) | Horizon language |
|--------|--------|----------------------|------------------|
| **core** | Cheap broad equity (or user-defined ballast) | `equity_broad`, sometimes plain `equity_style` | multi-year |
| **satellite** | Tilt, sector, factor, dividend, intl, bond ballast, income_option | sector / factor / dividend / intl / bond / income_option | years; review yearly |
| **tactical** | Short-horizon expression | `levered_long` only under product policy | days–weeks (not “hold forever”) |
| **avoid** | No investment path | `inverse`; broken/complex ETN when flagged | n/a |
| **cash_residual** | Unused monthly envelope / dry powder | — | until equity or ETF signal |

Bond / commodity: default **satellite** (ballast or macro), not equity core, unless user explicitly wants bond-heavy plan (still research framing).

---

## 3. Procedure

```text
1) Clarify goal (Givens)
   - growth total return / income cashflow / diversify / tactical expression
   - If missing, assume: long-horizon US equity total return + optional satellite tilts
   - Floating equity-first: stocks may take the month → ETF sleeves deferred

2) Assign each ticker (or placeholder role without ticker)
   - Start from M1 role_hint
   - Override: user wants SCHD as “dividend core” → allow core OR satellite with note
   - income_option → satellite + M5 required if not already run
   - levered_long → tactical only; never core
   - inverse → avoid

3) Build sleeve_map
   - List symbols (or “TBD”) per sleeve
   - Soft weight bands as **fractions of ETF sub-book or remaining envelope**, not % of net worth unless user gives AUM

4) Rebalance framework (no calendar order)
   - Drift bands example: core 60–100% of ETF sub-book; satellite 0–40%; tactical 0–10% and time-boxed
   - Rebalance trigger language: “when weights leave band or thesis breaks” — not “every Friday buy”

5) Capital split vs monthly envelope
   - remaining = monthly envelope − equities used − reserved
   - ETF deploy ≤ remaining
   - Prefer patient core over filling satellite first
   - Single-name priority may set ETF deploy = 0 this month

6) Emit counterfactuals: what moves a name core→satellite or satellite→avoid
```

---

## 4. Default weight bands (research defaults · soft)

For **ETF-only sub-book** (not whole net worth):

| Sleeve | Soft band of ETF sub-book | Notes |
|--------|---------------------------|--------|
| core | **60–100%** | One broad US or total-market style name often enough |
| satellite (sum) | **0–40%** | Cap single satellite name soft **≤ 50% of satellite bucket** |
| tactical | **0–10%** and temporary | Only levered long; M6 when filled; else warn stub |
| avoid | 0% | |

If user has **no tickers**, emit role-only plan:

```text
core: "US broad equity ETF (e.g. VOO/VTI-class) — pick via M3 on fees"
satellite: "optional sector/factor/income after M5/M1"
tactical: "empty unless explicit short-horizon levered ask"
```

---

## 5. Floating monthly envelope mapping

From `user-capital-policy.md`:

| Situation | ETF sleeve framework |
|-----------|----------------------|
| Strong single-name research path | ETF contribution **deferred**; sleeves unchanged as plan, deploy $ = 0 this month |
| Broad drawdown / stress (user or Brain notes) | May increase **core** ETF share of remaining envelope |
| Idle / no stock signal | Prefer **core** slices over chasing satellite narratives |
| Envelope residual small (<~$100) | Prefer single core name; avoid multi-satellite fragmentation |

Language:

```text
"Size core and satellite as fractions of cash the user stated this turn. Do not invent a $600–$1000 ceiling. Not a fixed DCA calendar."
```

Optional link to methodology “4% drop trigger” (engine method note): **only as rhythm**, amounts = envelope slices; not guaranteed.

---

## 6. Interaction with other modules

| Module | When |
|--------|------|
| M1 | Required for each named ticker |
| M2 | Prefer before locking core (ER check) |
| M3 | When choosing among core candidates or satellite peers |
| M5 | Any income_option in satellite |
| M6 | Tactical levered detail (if unfilled, tactical sleeve stays “policy-only warning”) |
| M7 | When to add vs wait (if unfilled, do not invent regime score) |
| etf-premium / liquidity | Brain-adjacent entry microstructure — not sleeve design |

---

## 7. Rebalance framework (templates)

### Drift-band

```text
If core weight of ETF sub-book < 60% due to satellite drift → research trim satellite / add core on next deploy.
If tactical held past stated horizon → research exit or hard re-justify (M6).
No automatic orders.
```

### Thesis-break

```text
Satellite exit research when: index methodology breaks thesis, user goal changes,
or income product fails M5 honesty (user expected uncapped upside).
```

### Tax / friction note

Mention only as research caveat (“turnover has tax/friction costs”) — not tax advice.

---

## 8. Confidence (L2 advisory)

| Condition | Ceiling |
|-----------|---------|
| Clear goals + classified tickers + capital note | A possible for **framework** |
| No tickers but coherent role plan | ≤ B |
| Heavy tactical / income without M5/M6 | ≤ C |
| Presented as “must allocate X% on date Y” | rewrite; conf not A |
| Inverse included as investable sleeve | blocked path |

---

## 9. Artifact shape (M4)

```text
artifacts.sleeve_map:
  core: [VOO]
  satellite: [SCHD, SMH]
  tactical: []
  avoid: []
  cash_residual_note: "remaining monthly envelope after equities"

artifacts.weight_bands_soft:
  core: "60-100% of ETF sub-book"
  satellite: "0-40%"
  tactical: "0-10% time-boxed"

artifacts.rebalance_framework: |
  Drift + thesis-break; no calendar orders.

artifacts.capital_split_framework: |
  Equity-first floating envelope; ETF deploy ≤ remaining;
  prefer core when idle.

artifacts.roles:
  VOO: core
  SCHD: satellite
  SMH: satellite

artifacts.modules_run: [..., M4]
capital_note: "floating envelope; not a fixed DCA"
```

---

## 10. Worked micro-examples

### A. Simple core-only

- Goal: long-term US equity, low effort  
- sleeve: core=[VOO-class], satellite=[], tactical=[]  
- M3 if choosing among VOO/IVV/SPY  

### B. Core + sector satellite

- core=[VTI-class], satellite=[SMH] ≤ 40% of ETF sub-book  
- Stress: satellite can dominate losses — state concentration  

### C. Income curiosity

- core=[VOO-class], satellite=[JEPI-class] + **M5**  
- Do not replace core with JEPI without explicit user accept of lag  

### D. User wants TQQQ as core

- Reject core assignment → tactical only; conf ≤ C if they insist “forever hold”  
- Point to product-policy / future M6  

---

## 11. Counterfactuals

- Single-name stock path consumes envelope → ETF map unchanged, deploy delayed.  
- User AUM grows far beyond $1k/month → bands stay structural; dollar examples scale with **stated** envelope, not invent NW.  
- Regime risk-off (when M7 exists) → raise core share of new capital framework.

---

*M4 · E-P2 · research framework only · floating equity-first capital*
