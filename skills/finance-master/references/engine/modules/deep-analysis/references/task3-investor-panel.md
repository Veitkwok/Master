# Task 3 · Investor panel (v4.5 US)

> **v4.5:** US methodologies only. No 50/65 multi-market panel, no Group E/F 游资, no LHB field whitelist.  
> Prefer Brain INVOKE → `investor-panel` skill; or run inline Top-10 / US-36 from `investor-frameworks.md`.

## Signal schema (per investor)

```text
investor_id, name, group, signal(bullish|neutral|bearish),
confidence 0-100, score 0-100, verdict,
reasoning (numbers), comment (in-voice),
pass[], fail[], ideal_price?, period?
```

## Modes

| Mode | Source | Count |
|------|--------|------:|
| Top-10 lite | `investor-frameworks.md` pick most relevant | 10 |
| US-36 | full frameworks file | ~36 |
| External panel skill | `UZI-Skill/investor-panel` RETURN | varies |

## Live groups (if using panel skill refs)

A value · B growth · C macro · D technical · G quant · I Serenity  

**Quarantined:** E 中国价投, F 游资, `lhb-analyzer`.

## Field focus by style (dim IDs)

| Style | Emphasize dims |
|-------|----------------|
| Buffett / Munger / Graham | D1, D8, D11, D15 |
| Lynch / Wood / growth | D1, D6, D8, D12 |
| Minervini / technical | D2, D12, D13 |
| Macro (Dalio/Soros/Marks) | D3, D8, D12 |
| Quant | D2, D8, D13 |
| Serenity | D5, D6, D11, D12 |
| Trap | D14 |

## Process

1. Select mode  
2. For each investor: apply **their** rules only  
3. Aggregate consensus % and Great Divide candidates  
4. Feed Stage 4 synthesis  

## Forbidden

- Loading LHB / 游资 / Group E–F / banned skills (auditor ban list)  
- Soft consensus that erases value-vs-growth war  

