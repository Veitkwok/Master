# M7 · Opportunity window（机会窗口）

**Module id:** `M7`  
**Status:** methodology filled (E-P3 · 2026-08-10)  
**Inputs:** user “buy the dip / should I add ETF / opportunity day”; Brain regime L0 (IBKR history, VIX note, optional breadth); optional valuation band **if** series pack exists  
**Outputs:** `opportunity_window` gate: `add_etf` | `wait` | `prefer_stocks` | `trim_satellite` | `no_new_risk`. The gate feeds `../../../../../contracts/advice-card.md`. Not a live order.  
**Links:** `../../../../docs/reference/methodology-metric-and-bands.md`; capital `../user-capital-policy.md`; exposure ideas distilled from research (claude-trading exposure-coach **concepts only**)

---

## 1. Purpose

Research gate: **given regime + (optional) relative valuation position + capital policy, what is the framework action for ETF capital this window?**  
Not an order. Not guaranteed mean-reversion.

---

## 2. Epistemic rules (hard)

| Rule | |
|------|--|
| Relative percentile ≠ intrinsic value | Bands are historical cheapness only |
| No series pack | **Do not invent** p20/p50/p80; use regime + capital only; mark `bands: unavailable` |
| Regime can break 10y bands | Always allow reliability downgrade |
| Equity-first | Strong single-name path → `prefer_stocks` even if bands look cheap |
| Guarantees | Forbidden (“must bounce”, “only lose time”) |

---

## 3. Inputs checklist

```text
1) Capital
   - remaining monthly envelope (user/Brain note or assume unknown → framework only)
   - equity_priority: true|false|unknown

2) Regime L0 (from Brain pack / IBKR / Web — do not fabricate)
   - index trend structure (e.g. vs MA50/200 if pack has history)
   - VIX / stress note if available
   - breadth / participation if Brain supplied (optional)
   - exposure_posture: risk_on | mixed | risk_off | unknown
     (synthesis label — see §4)

3) Product context
   - M1 class / role_hint for candidate ETF(s)
   - levered → M6; inverse → avoid path
   - income_option → M5 if yield-driven ask

4) Valuation bands (optional)
   - only if verified series: metric, p or zone (under/low_fair/high_fair/over)
   - invert_bands flag for DY/ERP
   - reliability: full_10y | short_window | regime_fracture_warning
```

---

## 4. Exposure / regime posture (distilled heuristics)

Inspired by process-OS “exposure before stock pick”. Concepts only — not a copy of external skill code.

| `exposure_posture` | Typical L0 cues (examples) | New risk stance |
|--------------------|----------------------------|-----------------|
| `risk_on` | Broad uptrend, calm vol, participation ok | Core adds allowed if capital free |
| `mixed` | Narrow leadership, elevated vol, mixed breadth | Prefer core over satellite; small size |
| `risk_off` | Breakdown, spiking vol, stress | Prefer wait / cash residual / stocks only if special |
| `unknown` | Missing pack | Default **wait** or **prefer_stocks** if user has equity thesis; conf ≤ B |

Do not require all cues; label unknowns in `fields_gap`.

---

## 5. Valuation zone → default research action

When bands **available** (equity, valuation_band_eligible):

| Zone (non-invert) | Default ETF research action |
|-------------------|------------------------------|
| under (<p20) | `add_etf` candidate (core first); still capital-gated |
| low_fair (p20–p50) | slow `add_etf` / compensation only |
| high_fair (p50–p80) | `wait` on new cash; hold ok |
| over (≥p80) | `trim_satellite` research / no new adds |

Invert metrics (DY/ERP): flip zone semantics per methodology doc.

When bands **unavailable**:

```text
bands: unavailable
action from regime + capital only
never fake percentile
```

---

## 6. Decision fusion (priority order)

```text
1) Inverse invest ask → no_new_risk + avoid (policy)
2) equity_priority true (Brain §10 path) → prefer_stocks
   (ETF map can stay; deploy $ deferred)
3) exposure_posture == risk_off → wait or no_new_risk
   (unless user only asks education)
4) levered_long ask → run M6; M7 may set wait if risk_off/mixed hostile
5) bands over + satellite → trim_satellite framework
6) bands under/low_fair + risk_on/mixed + capital free → add_etf (core preferred)
7) high_fair → wait on adds
8) unknown regime + unknown bands → wait; conf ≤ B
```

**Output action is a research gate**, not “market order.”

---

## 7. Rhythm mapping (optional · methodology 4% rewrite)

If user follows drawdown rhythm research:

```text
trigger: ≥4% drop from last research buy price (user-tracked)
AND zone allows new cash (under / low_fair or bands unavailable + not risk_off)
AND remaining envelope > 0
→ size = remaining / N_slices (N=5–10 soft)
```

Still **not** a fixed monthly DCA calendar.

---

## 8. Procedure

```text
1) Collect checklist §3; list gaps.
2) Assign exposure_posture (§4).
3) Assign valuation zone or unavailable (§5).
4) Fuse → action (§6).
5) Attach capital_note + which sleeve (M4) receives add (core default).
6) Counterfactuals: what L0 flips action within 1–4 weeks.
7) Emit opportunity_window string + struct.
```

---

## 9. Confidence (L2 advisory)

| Condition | Ceiling |
|-----------|---------|
| Regime L0 + capital clear; bands optional | B typical |
| Full bands + regime + capital | A rare; only if pack dense and no narrative stretch |
| Bands invented | **blocked** / rewrite |
| “Must buy the dip now” tone | rewrite; ≤ C |
| risk_off ignored to force add | ≤ C or blocked |

Multi-name opportunity screens: ≤ B until per-name packs close.

---

## 10. Artifact shape (M7)

```text
artifacts.opportunity_window_struct:
  asof: ...
  exposure_posture: risk_on|mixed|risk_off|unknown
  valuation:
    status: available|unavailable
    metric: pe_forward|...|null
    zone: under|low_fair|high_fair|over|null
    reliability: full_10y|short_window|regime_fracture_warning|null
  equity_priority: true|false|unknown
  remaining_envelope_note: "unknown|$x framework"
  action: add_etf|wait|prefer_stocks|trim_satellite|no_new_risk
  sleeve_target: core|satellite|tactical|none
  rhythm_note: null|"4% slice if user tracks"
  fields_gap: []

artifacts.opportunity_window: |
  <≤120 words clinical summary of gate + why>

artifacts.modules_run: [..., M7]
```

Parent RETURN_BLOCK `opportunity_window` field = same summary string.

---

## 11. Mini templates

### Prefer stocks

```text
Gate: prefer_stocks. Single-name research path can consume floating envelope;
ETF core map unchanged but new ETF cash deferred this window.
```

### Add core (bands under)

```text
Gate: add_etf → core. Relative valuation zone under (if pack) + posture not risk_off.
Size as fraction of remaining envelope; not a guarantee of mean reversion.
```

### Wait

```text
Gate: wait. Zone high_fair/over or posture risk_off/unknown without equity priority.
No new ETF cash framework; hold existing core unless thesis-break.
```

---

## 12. Counterfactuals

- VIX spike + breakdown → flip to wait/no_new_risk.  
- Bands pack arrives showing under → may unlock add_etf if capital free.  
- Strong stock idea appears → prefer_stocks even if ETF “cheap.”  
- Regime fracture note on 10y PE → downgrade band reliability; do not trust zone alone.

---

*M7 · E-P3 · research gate only · no fabricated percentiles · floating capital*
