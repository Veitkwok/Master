# 立场判定（stance）

> 输入 = 本轮数据包 + 引擎/worker 的分析输出；输出 = 唯一 stance。
> 优先级从高到低执行，命中即停。卡字段定义见 `references/contracts/advice-card.md`。

---

## 1. 输入

```text
last              本轮 IBKR 现价（必需）
target.base       目标价（可为 null）
target.high       目标区间上沿
invalidation      {price, thesis}（买入必需）
trap_level        green|yellow|orange|red|null
priced_in         not_priced|partial|priced|gap|null
confidence        A|B|C
position_context  ibkr|schwab|both|neither
data_gaps[]       关键缺口
user_cash        用户本轮说出的可投现金（无则 null）
```

缺失处理：`last` 或 `confidence` 缺失 → 直接 `WATCH`（已持有则 `HOLD`，只列不推）。
`target` / `invalidation` / `trap_level` / `priced_in` 缺失 → 对应门槛按"未通过"处理。

---

## 2. 判定优先级（逐条命中即停）

| # | 条件 | stance | action_cn |
|---|------|--------|-----------|
| 1 | 关键数据缺失（无现价 / 无置信度 / 分析 blocked） | 新仓 `WATCH`；已持有 `HOLD` | 观望 / 持有 |
| 2 | `trap_level` 橙或红 | 新仓 `AVOID`；已持有 `TRIM`（标注"陷阱风险，建议减仓评估"） | 回避 / 减仓 |
| 3 | 已持有，且 `invalidation` 已触发（价格或论点） | `SELL` | 卖出 |
| 4 | `last ≥ target.high` | 已持有 `SELL`；未持有 `AVOID`（已越过目标） | 卖出 / 回避 |
| 5 | `last ≥ target.base` | 已持有 `TRIM` | 减仓 |
| 6 | 未持有，`upside ≥ 20%` 且 `confidence ≥ B` 且 `trap ∈ {green,yellow}` 且 `priced_in ∈ {not_priced,partial}` 且 `invalidation` 完整 | `BUY` | 买入 |
| 7 | 已持有，`upside ≥ 15%` 且 `confidence ≥ B` 且 `trap ∈ {green,yellow}` 且无其他红线 | `ADD` | 加仓 |
| 8 | 已持有，其余情况 | `HOLD` | 持有 |
| 9 | 未持有，其余情况 | `WATCH` | 观望 |

补充规则：
- **target 质量**：只有质量 ≥B 的 target（worker 的 DCF/可比，或 `computed_comps.quality=ok/wide`）
  才能触发 #4/#5/#6/#7 的买入/减仓/卖出；`very_wide`/`insufficient` 的 target 只能
  展示与参考，**不能据此 BUY，也不能仅因价格到 target 触发 TRIM/SELL**。
- **target 触发的 TRIM/SELL 还要求卡片整体 confidence ≥B**；若 grade=C（例如极端 RSI、
  证据弱），即使现价 ≥ target，也只能 `HOLD`+写"target 已到但置信不足，转复核"，
  不能自动减仓/卖出。
- **买入硬校验**：出卡前必须用 `upside = target.base / last − 1` 重算一次；
  `BUY` 要求 `upside ≥ 20%`，`ADD` 要求 `≥15%`；不满足就只能 `WATCH/HOLD`。
  卡上 `upside_pct` 必须与重算结果一致（差 >0.5pp 视为不合格卡，重写）。
- **纯社交证据（grade C）**：永远不 `BUY`；未持有 → `WATCH`，已持有 → `HOLD`。
- **ETF**：产品/角色判断来自 `etf` 模块（M1–M7）；`target` 无 NAV/band 依据时
  不得 `BUY`，最多 `WATCH`。
- **重叠**：新买标的若与现有持仓/四张表同暴露，先按
  `references/contracts/book-and-overlaps.md` 判定"同一暴露不第二笔"；命中则 `WATCH`。
- **重复卡**：同票同日已出过卡且无新证据 → 不重复输出，摘要写"见今日该票卡"。

---

## 3. upside 与阈值

```text
upside = (target.base - last) / last   （target.base 缺失则无法计算）
新买最低赔率：20%（默认，写在 config）
加仓最低赔率：15%（默认）
买入上限 entry_limit 计算见 decisions/target.md §4
```

`entry_limit` 是"不追高"线：现价高于它 → 观望（`WATCH`），不是"分批追"。

---

## 4. 已持有 vs 未持有（动词不同）

| 状态 | 动词 |
|------|------|
| 未持有 | 买入 / 回避 / 观望 |
| IBKR 已持有 | 加仓 / 持有 / 减仓 / 卖出 |
| Schwab 已持有 | 同上，但卡上写"嘉信只读，需你手动执行" |
| 两边都有 | 合并数量展示，动作按合并仓判断，分别注明执行渠道 |

---

## 5. 输出（写进卡）

- `stance` + `action_cn`；
- 命中条目的编号与一句理由（例："#6 买入：+22.8% 上行、B、trap green"）；
- 若被否决：#2 陷阱 → 写哪条信号；#3 失效 → 写触发的是价格还是论点；
- `entry_limit` / `target` / `sell_plan` 按 target.md、sell.md 填。

---

## 6. 案例

- 未持有，target $224，last $182.4，+22.8%，B，trap green，partial，invalidation 完整
  → **BUY**，entry_limit = min(last×1.02, target×0.85) = min($186.05, $190.40) = $186.05 → 取整 $186.00。
- 已持有，last $230 ≥ target.base $224 → **TRIM**（减 1/3）。
- 已持有，trap red，last $180，target $224 → **TRIM**（陷阱风险）。
- 未持有，grade C（只有 X），target $224 → **WATCH**（不买）。
- 未持有，target null → **WATCH**（目标价缺失）。

---

*stance v1 · 命中即停 · 金币相关判断确定性化*
