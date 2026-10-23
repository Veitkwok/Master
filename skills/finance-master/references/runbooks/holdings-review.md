# Runbook · 持仓复核 routine（holdings）

> 适用：`holdings`，每个交易日 1 次（建议 08:30 +08，美股收盘后）。
> **不读 X。** 读 IBKR + Schwab 全量持仓 → 对照目标价/失效价/论点 → 给持有/加/减/卖。

---

## 1. 准备

1. S0 能力探测（重点 IBKR、Schwab、Hindsight、state、DeepSeek）。
2. 读 `state/runs`：今天是否已跑过 holdings？已跑过且用户未要求重跑 → 退出（幂等）。
3. 读 `state/advice`：今日 KOL routine 已出卡的票（这些仓不再重复送分析）。

---

## 2. 采集

1. IBKR：全部持仓（代码/数量/成本/现价/市值/浮盈亏%）。
2. 对触发分析的仓：**必须**做 Web 财务/财报日程查询，否则目标价只能 null。
2. Schwab：全部持仓 + 近期交易（只读；缺失则 skip）。
3. 对每个持仓：IBKR 现价 + 60–90 日线（失效价/结构用）。
4. 对每个持仓：Hindsight recall（上次 case 的 kill criteria / target / stance）。
5. watchlists 快照（只读）；不需要 X。

---

## 3. 逐仓判断（先轻后重）

对每个仓先做**轻量检查**（无需 worker）：

```text
触发分析 = 满足任一：
  - 相对成本浮亏 ≥ 20%
  - 按市值排名前 5
  - 用户本轮点名
  - 接近失效价（≤ 失效价 × 1.03）
  - 明日/本周有财报
  - 记忆 case 的 kill criteria 已触发
```

- 触发 → 进入 §4 完整分析；
- 不触发 → 只列表：代码、数量、成本、现价、浮盈亏%、`状态: 正常`、`review_by`。

**全部持仓都要出现在摘要里**（列表形式），不许漏仓。

---

## 4. 完整分析（≤3 个仓）

1. 按 `contracts/data-pack.md` 组包（该仓 + Web 最新事实/财报日程）。
   先读 `state/peers/YYYY-MM-DD.json`、`state/fundamentals/YYYY-MM-DD.json`
   同日缓存（命中则合并，不重复查）；未命中再查。
   **每只触发分析的仓必须逐票查 Web**：①股票统计页（shares_diluted / net_debt /
   eps 或 revenue / FCF）；②≥3 家 peers 倍数（PE/Fwd PE/EV-Sales/EV-EBITDA，带来源与 asof）；
   ③最新财报/事件。查到的值写进数据包并缓存 `state/fundamentals/`、`state/peers/`。
2. 写**全新** job 覆盖 `/workspace/master/jobs/current.json`（`mode=routine`，不复用旧 job），执行固定命令
   `/usr/bin/python3 -I -B /workspace/master/skill/scripts/deepseek_analyze.py`。
   **exit 8 → 按 missing[] 补采 → 重跑（最多 2 次）**；仍不齐加 `allow_incomplete:true`。
   exit 2–7 或审批卡住 → bot-inline（审批卡住则本 run 记失败、下轮补）。
3. worker → CONFIDENCE_BLOCK / CHALLENGE_NODES / 估值 / trap / priced-in。
4. 按 `decisions/sell.md` §3 判定：SELL / TRIM / HOLD / ADD / REVIEW；
   已持仓的失效规则用 §1.2（结构+论据+确认窗口），**不用**新买入的 15% 止损。
5. 按 `contracts/advice-card.md` 出卡（持仓上下文、成本、浮盈亏、卖出计划）。
6. 集中度：按 `decisions/sell.md` §2.1 计算 top-2 同主题占比，≥80% 必须标注。
7. 嘉信仓：卡上写"嘉信只读，需你手动执行"。

---

## 5. 特殊规则

- **深亏仓**（如 XYZ −90%）：触发条件是"论点是否还成立"，不是"能不能回本"；
  论点破裂 → SELL；论点未破但仓位过大 → TRIM。
- 没有目标的仓：不编目标价；只能给"继续持有/减仓/清仓"判断 + 缺口说明。
- 今日已给过卡的同票：摘要"见今日该票卡"，不重复送 worker。
- 不因为"长期看好"而忽略失效价；不因为"跌很多"而拒绝卖出（沉没成本）。

---

## 6. 输出

1. 持仓总表（全部仓，按市值排序）；
2. 逐仓卡（触发分析者，≤3）；
3. 今日触发汇总：`卖出 X 个 / 减仓 Y 个 / 持有 Z 个` + 集中度提示；
4. 下次复核日（review_by）；
5. 页脚"未下单 · 嘉信只读"。

---

## 7. 状态与失败

- 写 `state/runs`（`routine: holdings`）、`state/advice`（仅出卡仓）、`out/YYYY-MM-DD-holdings.md`。
- IBKR down → 输出"持仓不可用"，不编持仓；Schwab down → 只按 IBKR 判断并注明。
- 失败不重试；下一交易日补跑。
