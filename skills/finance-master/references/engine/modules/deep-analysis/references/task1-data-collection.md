# Task 1 · Data collection (v4.5)

> **v4.5:** No Python fetchers, no `.cache/raw_data.json`, no multi-agent script batches.  
> Brain supplies **DATA_PACK**; deep-analysis fills dims **D0–D14** from pack + gap-fill per `data-sources.md`.

## Goal

Produce a complete **fact layer** for one **US** ticker before valuation/panel.

## Order of operations

```
0. Confirm US ticker + contract_id (from pack or IBKR IBKR 合约解析)
1. Ingest data_pack → map into D0–D14 slots
2. List missing critical dims
3. Gap-fill within budget (IBKR then Web then X)
4. Emit dim table with source tags: CACHE | IBKR | WEB | X | DATA_GAP | DERIVED
```

## Critical vs optional

| Priority | Dims |
|----------|------|
| Critical | D0, D1, D2, D4, D8, D11, D12, D14 |
| Important | D3, D5, D6, D9, D13 |
| Optional | D7, D10 (skip if budget tight; mark gap) |

## Mapping pack → dims (examples)

| Pack key | Dims |
|----------|------|
| quote + stats | D0 (price context), D2, D8 |
| ohlcv.daily | D2 |
| themes_peers | D4, D6 hint |
| connections | D0, D5 |
| fundamentals_web | D1, D8 |
| social_x | D13, D14 |
| options_summary | D2/D13 support |

## Anti-patterns

- Serial 20 web searches for fields already in pack  
- Calling longbridge / yfinance / funda  
- Fetching A-share 龙虎榜 into D9 (use 13F / holders)  
- Spawning sub-agents to run deleted `scripts/fetch_*.py`  

## Done criteria

- [ ] Every dim D0–D14 has value or DATA_GAP  
- [ ] Sources tagged  
- [ ] Critical dims not all empty  
- [ ] Ready for Task 1.5 models (D15–D17)
