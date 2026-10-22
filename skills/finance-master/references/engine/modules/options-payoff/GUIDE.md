---
name: options-payoff
description: >
  Options strategy payoff analysis (legs, max P/L, breakevens).
  Brain-invoke only (sherlock INVOKE); do not trigger from casual user chat.
  finance-master v4.6.8.
version: 4.6.8
ecosystem: 4.6.8
metadata:
  tags: [finance, us-stocks, options, payoff]
  market_scope: US_EQUITIES_ONLY
  role: L2_TOOL
---

# Options Payoff · v4.6.8

## Consumer rules

- Underlying spot: pack or IBKR snapshot.  
- Structure: user-specified legs **or** IBKR `IBKR 期权参数` → `IBKR 期权链` (bound strikes) → leg snapshots for mid/IV if needed.  
- Payoff math: agent computation (see `references/bs_code.md` for formulas — implement in reasoning, no required local Python env).  
- Strategies catalog: `references/strategies.md`.  
- Brain §5 may interpret flow; this skill focuses on **structure PnL**, not alpha signals.  
- No yfinance option_chain requirement.

## Workflow

1. Confirm underlying + spot  
2. Normalize legs (right, strike, expiry, qty, debit/credit)  
3. Table: max profit, max loss, breakevens, pop qualitative  
4. Optional: simple BS value/Greeks if IV provided  
5. Text “payoff sketch” (ASCII or markdown table by underlying price grid)

```text

## L2 confidence (Cog-4 · advisory only)

`confidence` in `### RETURN_BLOCK` is **skill-local deliverable quality**, not user investment confidence.

| Rule | Max grade |
|------|-----------|
| `status: partial` or material `fields_gap` | **B** |
| X/social-only evidence for hard claims | **C** |
| `status: blocked` | no thesis A |
| Complete skill scope + hard sources + no material gaps | **A** allowed (still advisory) |

Default `confidence_scope` for this skill: **single_dim**.

Also emit Cog-4 fields when practical: `confidence_scope`, `confidence_basis` (evidence_independence, physical_mechanical, data_gaps_material), `limiting_factors`.

**Never** emit Brain `### CONFIDENCE_BLOCK` or `mode:` — the Central Brain re-grades via §H.6.

### RETURN_BLOCK
skill: options-payoff
status: ok|partial
ticker: SYM
confidence: A|B|C
confidence_scope: single_dim
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [legs, payoff_metrics]
fields_gap: [...]
artifacts:
  strategy_name: ...
  max_profit: ...
  max_loss: ...
  breakevens: [...]
  net_debit_credit: ...
counterfactuals: []
raw_notes: <≤250 words>
```

*v4.6.8 · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only*
