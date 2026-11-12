# 财报窗口：前瞻与复盘（earnings）

> 只作为**证据**写进卡；不自动改变 stance，不自动下单。
> 触发：持仓复核（holdings）里的持仓；KOL routine 不强制跑财报模块。

---

## 1. 触发窗口

| 模式 | 条件 | 输出 |
|---|---|---|
| 前瞻 `preview` | 财报日（confirmed 或 estimated）在 **未来 7 个自然日**内 | 预期 EPS/营收、历史 beat 率、隐含波动、关键看点 |
| 复盘 `review` | 财报已发布，且发布日在 **过去 3 个交易日**内（RTH） | 实际 vs 一致预期、指引变化、RTH/盘后反应 |
| 不触发 | 不在窗口 | 不写财报段，不因此报缺口 |

- 财报日期用公司 IR/交易所公告；estimated 要标 `estimated`。
- 已发布但没有可靠出处 → `status: unknown`，不猜数字。
- 盘前/盘后/夜盘反应单独列，**不计入 3 日失效确认**。

---

## 2. 数据要求

- 来源：公司新闻稿/IR（实际值）、至少一个一致预期来源（consensus）。
- 每个数字带来源 URL 与 `asof`；查不到就留空（`null`），不编。
- EPS 要标口径（GAAP / adjusted）；不一致时两个都写或写清用哪个。
- 指引：`raised | maintained | lowered | withdrawn | unknown`；"未给指引"写 unknown。
- 禁止使用训练数据/记忆里的旧财报数字。

---

## 3. 超预期/不及预期判定（带容差）

```yaml
earnings_surprise_tolerance:
  eps_pct: 1.0        # ±1% 内视为 inline
  revenue_pct: 0.5    # ±0.5% 内视为 inline
```

- `beat`：actual > consensus + tolerance；
- `inline`：在 ±tolerance 内；
- `miss`：actual < consensus − tolerance；
- `technical_miss`：低于 consensus 但在容差内 → 标 miss(technical)，**不构成退出条件**；
- 卡上写出具体差异百分比，用户自己判断是否"实质不及预期"。

## 4. 覆盖/失效关系

- 只有**实质 miss**（超出容差）或**指引下调/撤回**才写
  「⚠️ 覆盖退出条件已出现」；仍不自动改判、不下单。
- 财报好（beat + 上调）不自动撤销已确认的价格失效；覆盖是否继续由用户决定。
- 财报后价格反应只作证据；RTH 收盘才参与失效计数。

---

## 5. 卡面格式（写进卡片）

```text
财报: 2026-11-11 已发布（review）
EPS: 1.23 vs 1.20 预期（+2.5%，beat，adjusted）
营收: 1.52B vs 1.50B 预期（+1.3%，beat）
指引: 上调 2027（raised）
反应: RTH +24.7% | 盘后 +17%（另列，不计失效计数）
来源: <press release URL> / <consensus URL>（asof 2026-11-12）
覆盖退出条件: 未出现（miss/下调均未达容差阈值）
```
