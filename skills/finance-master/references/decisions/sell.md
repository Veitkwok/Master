# 卖出与失效（sell）

> 给出"什么时候卖、卖多少"。买入建议必须自带卖出计划；持仓复核必须逐仓检查触发。
> 与 `decisions/stance.md` 配合：stance 决定动作，本文件决定价格与节奏。

---

## 1. 失效条件（按仓位类型分开）

### 1.1 新买入 / 加仓（BUY / ADD 卡）

```text
candidates = []
若本轮 pack 提供 MA50 且 MA50 < last：candidates.append(MA50 × 0.99)
candidates.append(entry_limit × (1 − 15%))        # 入场风险预算
invalidation_price = round(max(candidates), 2)    # 取更紧（更高）的一档
若 invalidation_price ≥ last：不给买入
```

- 必须同时给：`invalidation_price` + `invalidation_thesis`（来自 CN 的可观测条件）。
- 触发任一 → 清仓（新仓）。

### 1.2 已持有（HOLD / TRIM / SELL 卡）

- **价格失效**：优先结构位（MA50 / MA200 / 前低 / 关键整数位），并写确认窗口：
  「连续 3 个交易日收盘低于 X」或「放量（≥1.5×20 日均量）收穿 X」。
- **论据失效**：趋势或基本面事件（指引下调、股息削减、订单取消、融资断裂等）。
- **不追溯套用新买入的 15% 入场止损**；长期持仓默认用结构 + 论据，除非用户显式
  配置 `max_drawdown_stop`（默认关闭）。深亏仓尤其不能用"回本"当持有理由。
  **Owner 决定（2026-10-23）：现有持仓不止损，继续持有**（配置见 `runtime/config.md`）。
- 没有目标价时，`sell_plan` 可以没有 ladder，但必须有
  `invalidation_price` + `invalidation_thesis` + `review_by`。

---

## 2. 卖出阶梯（默认）

| 触发 | 动作 |
|------|------|
| 现价 ≥ `target.base` | 减 **1/3**（分批止盈，落袋） |
| 现价 ≥ `target.high` | 再减 **1/3** |
| 剩余 1/3 | 用失效条件 + 下次复核守护；失效 → 全出；否则持有到复核日 |
| 任一失效条件触发（价格或论据） | **清仓**（卖出全部） |
| 论点被新证据推翻（未到目标价） | **清仓或降至观察仓**，写原因 |

- 用户偏好简单模式时：可改成"到 target.base 全出 + 失效全出"；默认用阶梯。
- 分批比例、止损百分比写在 pack `config`（默认 1/3、1/3、15%），不在卡上即兴发挥。
- 没有 target 时不编阶梯，只写"失效触发即全出"。

### 2.1 集中度（持仓复核必查）

- 计算 top-2 同主题/同因子（如 AI 开支、半导体、能源）占持仓市值比例；
- ≥80%，或单一持仓 ≥50% → 在摘要与 `risk.key_risks` 标注「集中度风险」；
- 不因此自动改变 stance，但要在卡上提示"可讨论减仓/对冲/提高现金"。
- 不用记忆里的旧持仓；以本轮 IBKR + Schwab 为准。

---

## 3. 持仓复核（holdings routine）

逐仓计算并给出动作：

```text
for each position:
  triggers = []
  if invalidation_price 触发（last ≤ 失效价）: triggers += "price_stop"
  if 论据失效（来自 memory 的 kill criteria / 本轮新闻）: triggers += "thesis_broken"
  if last ≥ target.base: triggers += "target_reached"
  if trap_level 橙/红: triggers += "trap_risk"
  if 与另一持仓同暴露: triggers += "overlap"
  stance = SELL | TRIM | HOLD | ADD | REVIEW
```

规则：
- 任一硬失效（price_stop / thesis_broken）→ **SELL**；
- target_reached → **TRIM**（阶梯）；trap 橙红 → **TRIM**（风险）；
- 浮亏 ≥20% 或市值前 5 或用户点名 → 送完整分析（DeepSeek worker）；
- 其余仓只列表：代码、数量、成本、现价、浮盈亏%、触发状态；**不编目标价**。
- 今日 KOL routine 已出过卡的票 → 摘要写"见今日该票卡"，不重复分析。

---

## 4. 嘉信（Schwab）仓位

- 只读：卡上写"嘉信只读，需你手动执行"。
- 可与 IBKR 合并判断（`position_context: both`），但执行渠道分开写。
- 不生成嘉信订单，不把嘉信仓写成 IBKR 草稿，不声称已卖出。

---

## 5. 复核节奏

- `review_by` = 下次财报日 或 `asof + 90 天`（取更早）。
- 到 review_by 未触发任何条件 → 重新评估论点，更新目标价/失效价，写新卡。
- 财报后必须重算 target 与 invalidation（不得沿用旧值）。

---

## 6. 案例（深亏仓，示意）

```text
XYZ：Schwab 10 股 @ $120.00，现价 $25.00（-79.2%），市值 $250.00
触发：thesis_broken（论点已破裂）+ price_stop（远低于失效价）
stance: SELL（清仓）
说明：下跌已远超止损区，继续持有的理由是"回本"而非论点 → 卖出；
      嘉信只读，需你手动处理；本卡不代下单。
```

---

## 7. 禁止

- 不因为"已经跌很多"而拒绝卖出（沉没成本）。
- 不在没有失效条件的情况下建议买入。
- 不把"目标价到了"当成必须全卖（默认分批）。
- 不写"保证卖在最高点"。

---

*sell v1 · 失效双轨 · 1/3 阶梯 · Schwab 只读*
