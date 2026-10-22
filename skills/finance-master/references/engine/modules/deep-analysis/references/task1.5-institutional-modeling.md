# Task 1.5 · Institutional modeling (v4.5 US)

> **v4.5:** Agent computes models in-context. No `lib/fin_models.py` / `compute_deep_methods.py`.  
> Dims: **D15 DCF · D16 Comps · D17 LBO** (plus narrative IC pieces inside D19 if requested).

## US default assumptions

| Param | Default | Source / note |
|-------|---------|----------------|
| rf | ~4.0% | 10Y UST (Web); update if pack has macro |
| ERP | 4.5–5.5% | US ERP band; state pick |
| beta | 1.0 or observed | sector override |
| tax | 21% + state adj. | ~25% blended if unknown |
| target debt weight | 10–30% | sector |
| pretax cost of debt | rf + credit spread | |
| stage1 growth | sector table | below |
| stage2 growth | ~half of stage1 toward terminal | |
| terminal g | 2.0–2.5% | ≤ long-run nominal GDP |

**WACC** = E/V × (rf + beta×ERP) + D/V × kd × (1−t). Show components.

### Sector growth / beta hints (US)

| Sector | stage1 g | beta tip | terminal g |
|--------|----------|----------|------------|
| Semis / AI hardware | 15–25% | 1.3–1.6 | 2.5–3% |
| Large-cap software | 12–20% | 1.1–1.4 | 2.5% |
| Consumer staples | 4–8% | 0.7–0.9 | 2–2.5% |
| Biopharma | 10–30% | 1.2–1.8 | 2% |
| Banks | 3–6% | 0.9–1.2 | 2% |
| Cyclicals (energy/materials) | −5–10% | 1.2–1.5 | 1.5–2% |
| Autoparts / EV supply | 10–25% | 1.3–1.7 | 2–2.5% |

## D15 · DCF

1. Build FCF path (explicit 5y + fade) from D1  
2. Terminal: Gordon or exit multiple — state which  
3. Equity value → per share (diluted shares from Web/pack)  
4. **Mandatory 5×5 sensitivity** (e.g. WACC × terminal g or stage1 g)  
5. Center cell must match base case  

If FCF ≤ 0 structurally: DCF `status: weak` — lean on D16; don’t fake precision.

## D16 · Comps

1. ≥3 US peers (IBKR themes/peers preferred)  
2. Multiples: PE, EV/Sales, EV/EBITDA as available  
3. Apply median/25–75% band to target metric → price range  
4. Adjust for growth/margin gap in words  

## D17 · LBO (optional stress)

- Entry at current price; leverage ~4–6× EBITDA if meaningful EBITDA  
- Exit year 5 at entry multiple ±1 turn  
- IRR / cash-on-cash; if IRR < ~15% under base, note “financial buyer unattractive”

## Present disagreement

```text
DCF (stage1 18%, WACC 9.5%): $X · ±Y% vs spot
Comps (EV/Sales median): $A–$B
LBO IRR: Z%
Conflict: ...
```

## Agent duties

- Override defaults when history CAGR or sector clearly differs — **log the override**  
- Never hide default vs adjusted as one number  
- No A-share tax (25% CIT) or CN 10Y as primary rf for US names  

## Legacy

Ignore script import examples and A-share parameter tables in older copies of this doc.
