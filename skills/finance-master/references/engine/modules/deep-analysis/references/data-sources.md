# Data sources · v4.5 field map (US)

> **Authority:** Brain `sherlock` **§D**. This file is the L2 mirror for deep-analysis gap-fill.  
> **Banned:** longbridge MCP, yfinance skill, funda skill, akshare, Playwright scripts, A-share 东财/龙虎榜 chains.

## Priority

```
SESSION_CACHE / data_pack → IBKR (market structure) → Web (fundamentals/narrative) → X (social) → DATA_GAP
```

Never parallel-fetch the same field from multiple stacks.

---

## Dim → field → source

| Dim | Fields (examples) | Tier-1 | Tier-2 |
|-----|-------------------|--------|--------|
| D0 profile | name, sector, description, products, geo | IBKR `IBKR 关联` / themes | Web company profile |
| D1 financials | revenue, EPS, margins, FCF, debt, ROE | — | Web 10-Q/10-K / IR / aggregator pages |
| D2 technical | OHLCV, MA20/50/200, RSI, Stage | IBKR `IBKR 历史K线` | Web chart summary |
| D3 macro | rates path, risk regime | IBKR index/futures if resolved | Web Fed/FRED commentary |
| D4 peers | peer tickers, relative multiples | IBKR `IBKR 主题` | Web peer comps |
| D5 chain | customers, suppliers, competitors | IBKR connections | Web supply-chain articles |
| D6 industry_tam | TAM, growth | — | Web industry reports |
| D7 costs_inputs | key inputs, commodity beta | IBKR CMDTY/futures optional | Web |
| D8 multiples | PE/PS/EV-EBITDA, 52w, perf | IBKR snapshot (`misc_statistics`, perf fields) | Web historical percentiles |
| D9 ownership | 13F, top holders | — | Web 13F / holders pages |
| D10 policy | regulation, antitrust, export | — | Web |
| D11 moat | qualitative score | derived | — |
| D12 catalysts | dated events | — | Web + X |
| D13 sentiment | ratings, social tone | IBKR not primary | Web ratings + X |
| D14 trap | 8 signals | pack quote for price-run | Web + X (see trap-detector) |
| D15–D17 | models | agent calc | inputs from D1/D8 |
| D18–D19 | risks / synthesis | agent | — |

---

## IBKR call recipes (US STK)

1. **Resolve:** `IBKR 合约解析(query=TICKER)` → pick exact `symbol` + US primary → `underlying_contract_id` / `contract_id`  
2. **Quote pack:** `IBKR 现价快照` with  
   `last, bid_ask, change, prior_close, open, high, low, volume, avg_90d_usd_volume, misc_statistics, cumulative_perf_*, year_to_date_change, implied_vol_underlying, underlying_today_option_volume, underlying_avg_option_volume` (subset OK)  
3. **Daily bars:** `IBKR 历史K线` `security_type=STK`, `step=ONE_DAY`, `period=ONE_YEAR` (or SIX_MONTHS), `outside_rth=false`  
4. **Themes:** `IBKR 主题(contract_id)`  
5. **Graph:** `IBKR 关联(contract_id, include=["link_info","company_info"])`  
6. **Options (optional):** `IBKR 期权参数` → `IBKR 期权链` (strike bounds) → snapshot on legs  

Do not display raw internal contract IDs to the end user.

---

## Web query templates

| Need | Example queries |
|------|-----------------|
| Statements | `"{TICKER} income statement revenue operating margin free cash flow"` |
| Guidance | `"{TICKER} latest earnings guidance transcript"` |
| Short interest | `"{TICKER} short interest short float days to cover"` |
| 13F | `"{TICKER} institutional ownership 13F"` |
| Targets | `"{TICKER} analyst price target consensus"` |
| Peers | `"{TICKER} vs {P1} {P2} valuation PE EV/Sales"` |

Max **1–2** queries per gap cluster when pack is partial.

---

## X templates

- `"{TICKER}"` min engagement for heat  
- `"{TICKER} (upgrade OR downgrade OR breakout OR bankruptcy)"`  
- Tip/trap language only when D14 / safety path  

---

## DATA_GAP policy

- Label the field `DATA_GAP`  
- Dependent conclusions confidence ≤ **B** (or **C** if core D1/D8 missing)  
- Never invent line items, short interest, or contract wins  

---

## Legacy note

Pre-v4.5 docs mentioning `lib/data_sources.py`, akshare, 东财, 龙虎榜 are **obsolete**. Ignore them if still present in other reference files.

**Never load:** banned deep refs (task2.5, task2-dimension-scoring, task3-agent-evaluation, multi-market fin-methods) — `../../../sherlock/references/banned-patterns.yaml`.  
**Pack schema:** Brain `../../../sherlock/references/data-pack-schema.md`.  
**IBKR (this L2):** market structure only. Account reads / drafts = Brain §D, not deep-analysis.
