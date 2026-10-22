# Liquidity Metrics Reference

> ⚠️ **v4.6.8 data fence:** Do **not** import or call yfinance, funda, longbridge, or opencli readers. Live path = Brain **DATA_PACK** → **IBKR MCP** → **Web/X**. Metrics below are methodology; field sources are mapped in **IBKR / DATA_PACK field map**.



Complete reference for all liquidity metrics, formulas, code templates, and interpretation guidelines.

---

## Table of Contents

1. [Bid-Ask Spread Metrics](#bid-ask-spread-metrics)
2. [Volume Metrics](#volume-metrics)
3. [Amihud Illiquidity Ratio](#amihud-illiquidity-ratio)
4. [Square-Root Market Impact Model](#square-root-market-impact-model)
5. [Turnover Ratio](#turnover-ratio)
6. [Composite Liquidity Score](#composite-liquidity-score)
7. [IBKR / DATA_PACK field map](#ibkr--data_pack-field-map)
8. [Edge Cases and Gotchas](#edge-cases-and-gotchas)

---

## Bid-Ask Spread Metrics

### Quoted Spread

The difference between the best ask and best bid price.

```
Absolute Spread = Ask - Bid
Relative Spread (%) = (Ask - Bid) / Midpoint × 100
Spread (bps) = (Ask - Bid) / Midpoint × 10,000
Midpoint = (Ask + Bid) / 2
```

### Effective Spread (estimated)

The effective spread captures the actual transaction cost, accounting for trades that execute inside the quoted spread. Without tick-level data, estimate as:

```
Effective Spread ≈ 2 × |Trade Price - Midpoint|
```

IBKR L1 snapshot has no tick tape; use the quoted spread as an upper bound. The effective spread is typically 60–80% of the quoted spread for liquid stocks.

### Spread as a Function of Price Level

Low-priced stocks often have wider percentage spreads due to the minimum tick size ($0.01). A $5 stock with a $0.01 spread has a 0.20% spread, while a $500 stock with a $0.01 spread has a 0.002% spread. Always report relative spread, not just absolute.

---

## Volume Metrics

### Average Daily Volume (ADV)

```python
adv = hist["Volume"].mean()
```

Use median for a more robust measure when volume has large spikes (earnings, index rebalancing).

### Average Daily Dollar Volume (ADDV)

```python
addv = (hist["Close"] * hist["Volume"]).mean()
```

Dollar volume is more meaningful than share volume for cross-stock comparisons because it normalizes for price differences.

### Relative Volume (RVOL)

```python
rvol = current_volume / avg_volume
```

| RVOL | Interpretation |
|---|---|
| > 3.0 | Extreme — likely news, earnings, or event |
| 1.5–3.0 | Elevated — increased interest |
| 0.8–1.2 | Normal |
| 0.5–0.8 | Below average — quiet day |
| < 0.5 | Very low — possible holiday, pre-event calm |

### Volume Coefficient of Variation

```python
volume_cv = hist["Volume"].std() / hist["Volume"].mean()
```

High CV (> 1.0) means volume is "spiky" — the stock alternates between very quiet and very active days. This matters for execution: you can't rely on the average volume being available every day.

### Intraday Volume Distribution

Volume follows a U-shape pattern in US equities — highest at open and close, lowest midday. Use 5-minute bars to visualize:

```python
# Use pack/IBKR FIVE_MINS bars (not yfinance). Example shape:
# bars = ohlcv.intraday_5m  # list[{ts,o,h,l,c,v}]
# group mean(v) by clock time within RTH
```

Typical distribution for US equities:
- **First 30 min (9:30–10:00)**: ~15–20% of daily volume
- **Midday (11:00–14:00)**: ~25–30% of daily volume
- **Last 30 min (15:30–16:00)**: ~15–20% of daily volume

---

## Amihud Illiquidity Ratio

### Formula

Amihud (2002) illiquidity ratio measures the daily price response per dollar of trading volume:

```
ILLIQ = (1/D) × Σ |rₜ| / DVOLₜ
```

Where:
- `D` = number of trading days in the period
- `rₜ` = daily return on day t
- `DVOLₜ` = daily dollar volume on day t (price × volume)

### Code

```python
returns = hist["Close"].pct_change().dropna()
dollar_volume = (hist["Close"] * hist["Volume"]).iloc[1:]  # align with returns

amihud_daily = returns.abs() / dollar_volume
# Remove inf values (zero-volume days)
amihud_daily = amihud_daily.replace([np.inf, -np.inf], np.nan).dropna()
amihud = amihud_daily.mean()

# Convention: multiply by 10^9 for readability
amihud_scaled = amihud * 1e9
```

### Interpretation

Higher values = less liquid. The ratio captures how much "price bang" you get per dollar of volume.

| Amihud (×10⁹) | Liquidity Level |
|---|---|
| < 0.01 | Mega-cap, extremely liquid (AAPL, MSFT) |
| 0.01–0.1 | Large-cap, highly liquid |
| 0.1–1.0 | Mid-cap, moderately liquid |
| 1.0–10 | Small-cap, less liquid |
| > 10 | Micro-cap, illiquid |

### Rolling Amihud

Track how liquidity changes over time:

```python
window = 20  # trading days
rolling_amihud = amihud_daily.rolling(window).mean() * 1e9
```

---

## Square-Root Market Impact Model

### Theory

The square-root law of market impact is one of the most robust empirical findings in market microstructure. Price impact scales with the square root of order size:

```
Impact (%) = σ × √(Q / V)
```

Where:
- `σ` = daily return volatility (standard deviation)
- `Q` = order size in shares
- `V` = average daily volume in shares

This means doubling the order size only increases impact by ~41% (√2 ≈ 1.41), not 100%. This concavity arises because large orders are typically split across time.

### Extended Model with Participation Rate

For orders executed over multiple periods:

```
Impact (%) = σ × √(Q / (V × T))
```

Where `T` is the number of days over which the order is executed.

### Total Execution Cost

```
Total Cost = Spread Cost + Market Impact
Spread Cost = 0.5 × Bid-Ask Spread (one way)
Total Round-Trip = 2 × (Spread Cost + Impact)
```

### Code for Impact Curve

```python
def impact_curve(price, adv_shares, daily_vol_sigma, sizes_pct_adv=None):
    # FENCED_v4.6.8: """Market-impact sketch from pack/IBKR inputs — no yfinance.
    price: last (IBKR/pack)
    adv_shares: average daily volume in shares (or convert from ADV USD / price)
    daily_vol_sigma: daily return stdev from pack ohlcv or history
    """
    if sizes_pct_adv is None:
        sizes_pct_adv = [0.1, 0.5, 1, 2, 5, 10, 20, 50]
    results = []
    for pct in sizes_pct_adv:
        frac = pct / 100
        shares = int(adv_shares * frac)
        impact_pct = daily_vol_sigma * (frac ** 0.5) * 100
        impact_per_share = impact_pct / 100 * price
        total_cost = impact_per_share * shares
        results.append({
            "pct_adv": pct,
            "shares": shares,
            "notional": round(shares * price),
            "impact_bps": round(impact_pct * 100, 1),
            "cost_per_share": round(impact_per_share, 4),
            "total_cost": round(total_cost, 2),
        })
    return results
```

---

## Turnover Ratio

### Formulas

```
Daily Turnover = Daily Volume / Shares Outstanding
Float Turnover = Daily Volume / Free Float Shares
Annualized Turnover = Daily Turnover × 252
Days to Trade Float = Float Shares / Average Daily Volume
```

### Shares / float (not from IBKR quote)

Shares outstanding and free float are **not** reliable IBKR snapshot fields for this skill. Prefer:

1. Brain pack / prior Web L0 if already filled  
2. Web (company IR, SEC, reputable data pages) when turnover vs float is required  
3. If unavailable → leave `fields_gap` and do not invent float

Float excludes restricted stock, insider holdings, and other locked-up shares. Float turnover is generally more informative than total turnover because it measures trading relative to the actually tradable supply.

### Interpretation

| Annualized Float Turnover | Interpretation |
|---|---|
| > 1000% | Hyper-active — meme stock, short squeeze, or speculative frenzy |
| 500–1000% | Very active — high retail or momentum interest |
| 100–500% | Actively traded — typical for popular large/mid-caps |
| 30–100% | Moderate — normal institutional holding pattern |
| 10–30% | Low — buy-and-hold investor base, limited trading |
| < 10% | Very low — thinly traded, possibly neglected or closely held |

---

## Composite Liquidity Score

For a quick single-number summary, combine normalized metrics:

```python
def liquidity_score(spread_pct, avg_dollar_volume, amihud_scaled, turnover_annual):
    """Returns 0-100 score. Higher = more liquid."""
    import numpy as np
    
    # Spread score (lower spread = higher score)
    spread_score = max(0, min(100, 100 - spread_pct * 200))
    
    # Dollar volume score (log scale)
    dv_log = np.log10(max(avg_dollar_volume, 1))
    dv_score = max(0, min(100, (dv_log - 4) / 6 * 100))  # $10K=0, $10B=100
    
    # Amihud score (lower = better)
    ami_score = max(0, min(100, 100 - np.log10(max(amihud_scaled, 0.001)) * 25))
    
    # Turnover score
    turn_score = max(0, min(100, turnover_annual / 5))  # 500% annual = 100
    
    # Weighted composite
    composite = (
        spread_score * 0.30 +
        dv_score * 0.35 +
        ami_score * 0.20 +
        turn_score * 0.15
    )
    return round(composite, 1)
```

This is a heuristic, not a formal measure. It's useful for quick comparisons but should not replace examining individual metrics.

---

## IBKR / DATA_PACK field map

> **No banned data skills.** Prefer Brain pack → IBKR snapshot/history → Web for shares/float if needed.

### From pack `quote` / IBKR `IBKR 现价快照`

| Field | Description | Used for |
|-------|-------------|----------|
| `bid` / `ask` (bid_ask) | Best bid/ask | Spread |
| `last` | Last trade / mark | Impact, mid |
| `open` / `high` / `low` | Session OHLC when available | Intraday |
| `volume` | Session volume | RVOL |
| `avg_90d_usd_volume` | ADV in USD | Liquidity grade |
| `prior_close` | Prior close | Change |
| `implied_vol_underlying` | Underlying IV | Options context |

### From pack `ohlcv` / IBKR `IBKR 历史K线`

| Column | Description |
|--------|-------------|
| `o` / `h` / `l` / `c` | Open/high/low/close |
| `v` | Volume |
| `date` or `ts` | Bar timestamp |

### From IBKR option surface (optional)

| Source | Fields | Used for |
|--------|--------|----------|
| `IBKR 期权链` + leg `IBKR 现价快照` | bid/ask, volume, OI, mid IV | Options liquidity |

### From Web (only if pack gap)

| Need | Source |
|------|--------|
| shares outstanding / float | filings / IR |
| market cap | derived last × shares or Web |

Mark any Web fallback in `fields_gap` / conf limiting.

---

## Options Spread Analysis

Analyze near-the-money options spreads from the nearest expiration via **IBKR** (`IBKR 期权参数` → `IBKR 期权链` + leg snapshots):

- Prefer ATM ± a few strikes on nearest listed expiry  
- Spread = ask − bid; report bps vs mid  
- If chain unavailable → `fields_gap`, do not invent OI/volume  

---

## Order Book Depth Proxy

IBKR L1 snapshot is **not** full Level 2. Depth proxies:

| Signal | Source |
|--------|--------|
| Top of book bid/ask (+ size if present) | IBKR snapshot |
| Intraday volume U-shape | pack/IBKR `FIVE_MINS` history |
| Options OI / volume | IBKR option surface (bounded) |

Never claim full book depth from free web quotes.

---

## Edge Cases and Gotchas

### Zero-Volume Days

Some thinly traded stocks have days with zero volume. Filter these before computing Amihud (division by zero) and volume averages:

```python
# Remove zero-volume days for Amihud
mask = hist["Volume"] > 0
hist_filtered = hist[mask]
```

### Pre/Post Market Data

Extended-hours prints have wider spreads and lower volume. For liquidity analysis prefer **regular-session** IBKR history bars and RTH-aware snapshot fields; if outside RTH, use prior RTH history (Brain Step 0 outside-RTH rule) and label `asof`.

### Quote Staleness

Snapshots can be marks or prior close outside RTH. During market hours, treat bid/ask as L1 only (not full book). Note session vs history source in output.

### ADRs and Foreign Stocks

American Depositary Receipts (ADRs) may show different liquidity than the underlying foreign-listed stock. The ADR spread can be wider than the home-market spread. When analyzing ADR liquidity, note this distinction.

### ETFs vs. Stocks

ETF liquidity is more complex — the ETF may appear illiquid (low volume, wide spread) but the underlying basket is very liquid, meaning authorized participants can create/redeem shares efficiently. The "true" liquidity of an ETF is the liquidity of its underlying holdings. Note this when the user asks about ETF liquidity.

### Penny Stocks (< $1)

Minimum tick size ($0.01) creates a floor on absolute spreads. A $0.50 stock can't have less than a 2% spread (at minimum tick). Relative spread metrics are especially important for low-priced securities.

### Weekend/Holiday Gaps

Volume averages should use **trading days only** (IBKR history bars / pack OHLCV). When computing "days to trade float", use trading days, not calendar days.
