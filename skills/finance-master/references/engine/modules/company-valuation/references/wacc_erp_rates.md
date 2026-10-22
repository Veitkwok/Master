# WACC, ERP, Risk-Free Rates & Sector Benchmarks

> ⚠️ **v4.6.8 data fence:** Do **not** `import yfinance` / `pip install` / call `yf.*`.  
> Live path: Brain **DATA_PACK** → **IBKR MCP** → **Web** (FRED / Damodaran / filings).  
> Snippets take numeric inputs already in-pack or from Web text — no broker-like install loops.

Reference values for cost-of-capital inputs. Prefer live values over these defaults when available.

## Risk-Free Rate

Use the 10-year sovereign yield of the company's reporting currency.

| Market | Instrument | How to obtain (v4.6.8) | Typical range |
|--------|------------|------------------------|---------------|
| US | 10Y Treasury | Web (FRED / Treasury) or pack `wacc_hints.rf` | 3.5–5.0% |
| UK | 10Y Gilt | Web (BoE / FRED) | 3.0–4.5% |
| Germany | 10Y Bund | Web (ECB) | 2.0–3.5% |
| Japan | 10Y JGB | Web (BoJ) | 0.5–1.5% |

**Live (agent procedure — no yfinance):**

```text
1. Prefer data_pack.wacc_hints.rf if present
2. Else Web: latest US 10Y yield (decimal form, e.g. 4.2% → 0.042)
3. Else default rf = 0.045 and flag stale in RETURN fields_gap / limiting_factors
```

```python
def resolve_rf(data_pack, web_rf=None, default=0.045):
    """rf from pack or Web number — never Yahoo Ticker objects."""
    pack_rf = (data_pack.get("wacc_hints") or {}).get("rf")
    if pack_rf is not None:
        return float(pack_rf), "PACK"
    if web_rf is not None:
        return float(web_rf), "WEB"
    return default, "DEFAULT_STALE"
```

## Equity Risk Premium (ERP)

Use Damodaran's monthly ERP update (damodaran.nyu.edu) as anchor when Web-available. Intra-year, **~5.0–5.5%** is a reasonable US mid-range for finance-master.

| Market | ERP (default) | Source |
|--------|---------------|--------|
| US | 5.0–5.5% | Damodaran implied ERP (S&P 500) |
| Developed Europe | 6.0–6.5% | Country risk + base ERP |
| Japan | 6.0% | Country risk + base ERP |
| Emerging (if forced multi-mkt) | 7.5–10% | Base + CRP — **product default is US-only** |

```
ERP_country = ERP_mature + CRP
```

## Cost of Debt

**Preferred:** `interest_expense / total_debt` from Web filings / pack fundamentals.

**Fallback:** credit rating spreads over risk-free rate (table assumptions — label as estimate).

## Beta

| Source | Use |
|--------|-----|
| pack / IBKR-derived proxy | Prefer |
| Sector median Web | Fallback |
| 1.0 | Last resort; flag gap |

## WACC assembly

```
WACC = we * (rf + beta * ERP) + wd * kd * (1 - tax)
```

Show components in RETURN artifacts. Never hide defaulted rf/ERP.

## Defaults (US, when gaps)

| Param | Default | Flag |
|-------|---------|------|
| rf | 4.5% | stale if not Web/pack |
| ERP | 5.0–5.5% | |
| tax | 21% federal + state adj. | |
| terminal g | 2.0–2.5% | |

---

*v4.6.8 · pack/Web rates · yfinance fenced*
