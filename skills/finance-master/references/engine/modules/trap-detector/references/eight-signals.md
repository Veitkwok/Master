# Trap detector · 8 signals (v4.5)

> Used by `../GUIDE.md`. All market data via **Brain Data Pack**, **IBKR MCP**, or **Web**.  
> **Banned:** `fetch_financials`, `fetch_sentiment`, `fetch_kline`, `fetch_capital_flow`, akshare, longbridge, yfinance skill, funda skill.

---

## Signal 1 · Coordinated low-quality accounts

**Hit when (any 2):**
- Web/X shows many near-identical “buy {name}” posts in 7–30 days  
- Accounts look new / low engagement / bot-like  
- Same copy-paste target price or emoji stack across handles  

**Collect:** 3–5 example URLs or post IDs + rough timing.

**Tools:** `web_search`, X keyword/semantic search.  
Query seeds: `"{TICKER} buy"`, `"{name} 推荐"`, `"{TICKER} moon"`, `"{TICKER} target"`.

---

## Signal 2 · Template hype language

**Hit when ≥2 distinct templates appear** in tip content:

| CN | EN |
|----|-----|
| 即将爆发 / 重大利好 | “about to explode”, “massive catalyst” |
| 主力建仓完毕 / 庄家洗盘结束 | “smart money loaded”, “accumulation done” |
| 目标翻倍 / 最后上车 | “double from here”, “last chance” |
| 内部消息 / 知情人 | “insider”, “I know someone” |
| 底部反转 / 技术面突破 | “breakout confirmed” (with no chart substance) |

---

## Signal 3 · Paid group / VIP funnel

**Hit when:**
- Mentions of paid Discord/Telegram/WeChat VIP, “加群”, live-stream stock tips tied to the name  
- QR / invite links next to the ticker pitch  
- “Signal group” upsell as the main CTA  

**Tools:** Web search `"{name} VIP"`, `"{TICKER} Discord signals"`, `"{name} 直播间"`, `"{name} 微信群"`.

---

## Signal 4 · Fundamentals vs hype disconnect

**Hit when (any):**
- Loss-making or ROE very weak **and** social volume spike  
- Clear sector downcycle **and** aggressive “must buy” campaign  
- Aggressive growth claims with no public filing support  

**Data (in order):**
1. Brain `data_pack.fundamentals_web` / quote context  
2. Else **one** Web search: `"{TICKER} revenue profit ROE market cap"`  
3. Heat: X search volume / Web “why is {TICKER} trending”  

**Do not** invent financials. If missing → `data_gap` (does not count as hit unless hype is extreme **and** user keyword boost ≥2).

---

## Signal 5 · Price already ran into the tip

**Hit when (any):**
- ~30–60d (or ytd) return ≳ +40–50% **before** tip cluster  
- Tip wave coincides with climax volume / vertical extension  
- Large gap-up into tip day with no new primary filing  

**Data (in order):**
1. Brain Data Pack: last, prior performance, 52w, volume  
2. Else IBKR: `IBKR 现价快照` (`change`, `cumulative_perf_*`, `misc_statistics`, `volume`) + optional `IBKR 历史K线` `ONE_DAY` / `ONE_MONTH`  
3. Else Web: `"{TICKER} stock performance 1 month"`  

**Banned:** `fetch_kline`, `fetch_capital_flow`.

---

## Signal 6 · Guru / “teacher” persona

**Hit when:**
- “X 老师 / 股神 / 操盘手 / signal coach” pushing the name  
- Lifestyle flex (cars, fake PnL screenshots) without verifiable track record  
- Pressure to trust the person over filings  

**Tools:** Web + X `"{name} 老师"`, `"{TICKER} signals group"`, `"{name} 股神"`.

---

## Signal 7 · Cross-platform blast

**Hit when** same pitch appears on **≥3** distinct platforms within ~2 weeks, e.g.:
- X / Twitter  
- Reddit (via Web)  
- TikTok / 抖音 / YouTube (via Web)  
- Telegram/Discord mention pages  
- Blog/WeChat reposts  

Single-platform organic chatter alone is **not** a hit.

---

## Signal 8 · Fake research / forged news

**Hit when:**
- Company or reputable outlet **denies** rumor  
- “Research PDF” without broker, analyst, or date  
- Fabricated partnership / contract claims circulating with tip flow  

**Tools:** Web `"{TICKER} rumor"`, `"{TICKER} denies"`, `"{name} 辟谣"`, `"{name} 澄清"`.

---

## Keyword boost (user text)

| Match | Add to effective hit count |
|-------|----------------------------:|
| 朋友推荐 / 群里 / 老师 / friend / group tip | +1 |
| 内幕 / 稳赚 / guaranteed / insider | +2 |
| 必涨 / 翻倍 / easy money | +1 |

## Level map

| Effective hits | trap_score | level |
|----------------|------------|-------|
| 0–1 | 9–10 | 🟢 |
| 2–3 | 6–8 | 🟡 |
| 4–5 | 3–5 | 🟠 |
| 6+ | 1–2 | 🔴 |

`trap_score` is **higher = safer** (legacy convention).
