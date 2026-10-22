# User capital envelope (owner policy · research framing)

Master copy: do not apply the table below to existing IBKR or Schwab positions. Read the live book in `../../../../contracts/data-pack.md`. Use a monthly cash figure only after the user states one. Watchlist reads are part of the routine.

**Owner:** Veit  
**As of:** 2026-08-10  
**Nature:** soft product defaults for sizing **frameworks** — not broker limits, not advice.

## Monthly investable cash (USD)

| Bound | Value | Notes |
|-------|------:|-------|
| Practical **ceiling** | **1000** | Should not plan as if more is reliably available |
| Common range | **600–1000** | Varies month to month |
| Floor | **0–600** | Possible; do not assume full 1000 every month |

## Floating allocation (critical)

The dollar table above is historical (as of 2026-08-10). Do not speak it as this book's ceiling.

1. Existing IBKR and Schwab positions are read from `../../../../contracts/data-pack.md`. Do not size them down to a monthly envelope.  
2. A new buy is sized only after `../../../../contracts/advice-card.md`, and only with a cash figure the user stated in this conversation.  
3. Single-name priority and a broad drawdown still describe when ETF cash might wait or increase. They do not invent the dollar amount.

Do not say “up to ~$1000” unless the user stated that number. Never say the user must invest a fixed sum into one ETF on a named date.

## Watchlists

Read Favorites, ETFs, Assets, Nasdaq-QQQ, and Candidate from the pack. Do not require a pasted export. Do not mutate the first four.

## Coupling to Sherlock

The pack keeps no persistent capital cache; the Brain `SESSION_CACHE` may exist but stores no cash ceiling. Grouping for this book is the skill entry's book-and-overlaps contract.
