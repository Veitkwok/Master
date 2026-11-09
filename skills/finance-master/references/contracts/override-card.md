# Override 决策卡（人工覆盖记录）

> 用途：当规则要求 `SELL`（失效触发）或 `TRIM`（target/陷阱触发），但**用户明确决定暂时不执行**时，
> 必须留下这张卡。它不改变原卡，不重新分析，只记录"我知道规则要求什么、我选择什么、为什么、
> 到什么时间/条件必须重新评估"。
>
> **只有用户在有人的对话里明确确认才能生成；routine 不得自行 override。**

---

## 1. 什么时候需要

| 原动作 | 情况 | 需要 override？ |
|---|---|---|
| SELL（invalidation 触发） | 用户决定 HOLD 或只 TRIM | ✅ 必须 |
| TRIM（target 触发） | 用户决定继续 HOLD 到更高目标 | ✅ 必须 |
| TRIM（trap 橙/红） | 用户决定不减 | ✅ 必须 |
| BUY / ADD | 任何情况下想绕过规则加仓 | ❌ 不允许 override；只能等规则满足 |
| WATCH | 想直接买 | ❌ 不允许；必须走 BUY 条件 |

其他硬红线（下单/写 watchlist/发邮件/不得用 very_wide target 买入）**不可 override**。

---

## 2. 机器可读格式（写进 `state/advice/YYYY-MM.jsonl`）

```yaml
type: override
override_version: 1
override_id: ovr-CRWV-20261109            # ovr-<SYMBOL>-<YYYYMMDD>
asof: 2026-11-09T18:30:00+08:00
symbol: CRWV
routine: holdings | adhoc
base_card:
  path: /workspace/master/out/cards/2026-11-09/CRWV.md
  asof: 2026-11-09T08:35:00+08:00
triggered_rule: invalidation.price | invalidation.thesis | target | trap
trigger_evidence: "11-04/05/06 连续 3 个 RTH 收盘 48.42/43.66/46.40 < 53.50"
default_action: SELL | TRIM
override_decision: HOLD | TRIM
override_reason: fundamental_improvement | earnings_pending | thesis_intact | tax_or_liquidity | other
override_reason_text: "一句可证伪的覆盖理由"
evidence: ["来源/日期/链接（不许用训练数据）"]
risk_ack:
  additional_downside: "再跌 X% 的承受说明"
  concentration: "top2 占比 X%"
  event_risk: "11-10 财报"
position:
  ibkr_qty: 0
  schwab_qty: 0
  cost_basis_note: null
review_by: 2026-11-20T23:59:59-05:00       # 必须 ≤ 30 天 / 不超过下一次财报后 5 个交易日
exit_now_conditions:
  - "RTH 收盘 < 40.00"
  - "财报指引下调"
  - "出现新的硬失效"
reset_invalidation: false                  # true 时须给出新的 invalidation_price/thesis
new_invalidation: null
status: active | expired | superseded | executed
user_confirmed: true
confirmed_at: 2026-11-09T18:30:00+08:00
order_sent: false
schwab_trade: forbidden
```

---

## 3. 卡面展示格式（写进 `out/` 与摘要）

```text
## CRWV · 覆盖决策 · HOLD
原始卡: 2026-11-09 CRWV（SELL / 失效触发）
触发: 失效（连续 3 日 RTH 收盘 < $53.50：11-04 $48.42 / 11-05 $43.66 / 11-06 $46.40）
默认动作: SELL（剩余仓位全出）
覆盖决定: HOLD
覆盖理由: thesis_intact — 11-10 财报前不裸卖，等财报确认再执行
风险接受: 财报前再跌 20% 可承受；集中度 CRWV+VST 89.8% ⚠️
立即退出条件: RTH 收盘 < $40 / 财报指引下调 / 新硬失效
复核截止: 2026-11-20（到期未复核 = 自动恢复 SELL）
状态: active（1/2 次覆盖）· 用户已确认 · 未下单
```

---

## 4. 规则

1. **必须引用原卡**（path/asof），原卡不删不改；override 是追加记录。
2. `review_by` 必填，且 **≤30 天**；跨财报必须把财报设进复合日期。
3. 到期未复核 → 状态 `expired`，原规则自动恢复；日检 FAIL(override_expired)。
4. **同票同失效 30 天内最多 2 次 override**；第 3 次必须由用户重写论点并重新跑分析，不能继续覆盖。
5. override 不能升级动作：不能从 SELL 改成 ADD/BUY；不能绕过 target 质量买入。
6. 持仓集中度 >80% 时 override 必须写 `risk_ack.concentration`，否则无效。
7. 每张 override 必须 `sync_retain` 一条 `OVERRIDE-<TICKER>-<YYYYMMDD>` case。
8. 用户没明确说"确认覆盖"→ 不得生成；Bot 只能"建议选项"，不能替用户决定。

---

## 5. 日检规则

- 失效已触发、原卡为 SELL，但当日摘要/状态是 HOLD/TRIM → 必须有有效 override（active 且未过期）；
  没有 → `FAIL(missing_override)`；
- override 已过期仍按覆盖状态操作 → `FAIL(override_expired)`；
- override 数量/理由/风险接受字段缺失 → `FAIL(invalid_override)`；
- 有有效 override → 记 `OVERRIDE` 状态（不算 FAIL），摘要写明"人工覆盖，非系统信号"。
