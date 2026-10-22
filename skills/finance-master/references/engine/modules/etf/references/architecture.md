# ETF skill · Architecture

**Package path:** `etf` (top-level L2 — **not** under `finance-skills/`)  
**Orchestrator:** `sherlock` via §9 / §H  
**Status:** E-P1–E-P4 **done** — M1–M7 methods + Val-1 GP07/08 / NEG11/12

---

## Why top-level

| Choice | Reason |
|--------|--------|
| Outside `finance-skills/` | Hermes-watched folder layout **frozen**; no nested ETF branch there |
| Separate from `etf-premium` | Premium is a **single-dim entry check**; this skill is plan + product research |
| Name `etf` | Short route id: `etf` |

```text

├── etf/                         ← this skill (plan + research)
└── finance-skills/
    └── etf-premium/             ← adjacent: NAV premium snapshot only
```

---

## Layers

```text
User ETF intent
    → Sherlock §9
        → INVOKE etf
            → modules M1–M7 (on demand)
            → optional Brain also INVOKE etf-premium / stock-liquidity
        → §H.6 re-grade → user CONFIDENCE_BLOCK (Brain-owned)
```

L2 **does not** call L2. Only Brain composes multi-skill turns.

---

## Module map

| Id | Name | Inputs | Outputs (artifacts) | Status |
|----|------|--------|---------------------|:------:|
| **M1** | Taxonomy | ticker or description | `class`, `reset_horizon`, `role_hint`, `metric_hint` | **filled** → `modules/m1-taxonomy.md` |
| **M2** | Product card | ticker + Web/issuer + IBKR quote | fees, AUM?, holdings?, ER, distribution note | **filled** → `modules/m2-product-card.md` |
| **M3** | Compare / screen | 2–N tickers | table: fee, role, overlap proxy, gaps | **filled** → `modules/m3-compare.md` |
| **M4** | Core–satellite | goals + risk + optional weights | sleeve map; rebalance **framework** only | **filled** → `modules/m4-core-satellite.md` |
| **M5** | Income honesty | distribution ETFs | dist rate vs total-return risks; no yield guarantees | **filled** → `modules/m5-income-honesty.md` |
| **M6** | Tactical levered long | e.g. TQQQ | short-horizon only; decay / path risk; **no inverse** | **filled** → `modules/m6-tactical-levered-long.md` |
| **M7** | Opportunity window | regime L0 (IBKR history, VIX note…) | research gate: add / wait / prefer stocks; **not** order | **filled** → `modules/m7-opportunity-window.md` |

**Adjacent (not this package):**

| Skill | Use |
|-------|-----|
| `etf-premium` | Premium/discount + tradability color before entry |
| `stock-liquidity` | Spread / ADV / impact sketch |
| `sepa-strategy` market-environment refs | Regime ideas for M7 (read-only methodology) |
| `stock-correlation` | Price co-movement; **not** holdings overlap |

---

## Data plane

| Need | Source |
|------|--------|
| Price, history, ADV, bid/ask, positions | This turn's pack from `../../../../contracts/data-pack.md` (IBKR; Schwab positions read-only) |
| NAV / iNAV | Web / issuer (often DATA_GAP) |
| Holdings, ER, index | Issuer / SEC / reputable Web |
| Watchlists | Favorites, ETFs, Assets, Nasdaq-QQQ, Candidate from the same pack. Read-only except Candidate after the user confirms. |

Banned: yfinance, funda, opencli readers, live order submit, Schwab orders. Do not mutate Favorites, ETFs, Assets, or Nasdaq-QQQ.

---

## Capital envelope (product-level)

See `user-capital-policy.md`. Do not apply the historical $600–$1000 table to the existing book. Size a new buy only if the user states a cash figure, and only on the advice card. Sleeve frameworks are inputs to `../../../../contracts/advice-card.md`, not a second order.

---

## Implementation phases

| Phase | Deliverable | Status |
|-------|-------------|:------:|
| P0 | Scaffold + Brain routing | **done** |
| **P1 / E-P1** | M1 + M2 + M5 methodology | **done** 2026-08-10 |
| **P2 / E-P2** | M3 compare + M4 core–satellite | **done** 2026-08-10 |
| **P3 / E-P3** | M6 levered long + M7 opportunity window | **done** 2026-08-10 |
| **P4 / E-P4** | Eval GP07/GP08 + NEG11/12 under dev evals | **done** 2026-08-11 |

---

*Architecture + M1–M7 methods · no live order · no yield guarantees · stance is ../../../../contracts/advice-card.md*
