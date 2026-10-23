# 运行时 · 交付（delivery）

> routine 结果默认只在 Bot 聊天里；同时落 `/workspace/master/out/`。
> 不发邮件（逐封审批，不适合无人值守）；Page 可选、仅在用户在场时发布。

---

## 1. 一次 run 的交付物

1. **聊天摘要**（≤ 60 行）：状态行 + 卡（≤2 张）+ 观察 + Candidate 提议 + 缺口 + 页脚；
2. **文件**：`/workspace/master/out/YYYY-MM-DD-<routine>.md`（完整摘要 + 卡）；
3. **卡片文件**：`/workspace/master/out/cards/YYYY-MM-DD/<SYM>.md`；
4. **状态**：`state/runs`、`state/advice`、`state/mentions` 已写。

---

## 2. 摘要模板

```text
📅 2026-10-23 · primary_babybus · 07:32 +08
运行: succeeded · partial（原因：Hindsight 不可用 / 3 票估值 blocked）
数据: IBKR✅ X✅(1 read) Hindsight❌ Schwab skip DeepSeek✅(cache 29k hit)
结果: 3 只候选 → 2 张卡 + 1 只观察

## NVDA · 买入（新买）
现价 $182.40 | 买入上限 $186.00 | 目标 $224（区间 $205–$243，6–12m）
卖出: $224 减 1/3 → $243 再减 1/3 → 失效 $158 全出
证据: B（IBKR+Web）| trap green | priced_in partial
缺口: 无

## MRVL · 观望
目标价缺失（估值输入不足：fundamentals.gross_margin）
不买；下轮补数据。

Candidate 提议: NVDA 14日3次/2账号/high → 回复确认后写入
缺口: 无
未下单 · 未写观察列表（Candidate 待你确认）
```

- `运行:` 行必须写 run 状态（succeeded/partial/failed）+ partial 原因（Hindsight/估值/
  Web 缺失/审批），不要只写"成功"；**没有这一行 = 摘要不合格，重写**。
- 持仓卡加两行：`集中度: top2 同主题 X% ⚠️`（≥80%）与
  `⚠️ 接近失效: 差 X%（连续 3 日中的第 N 日）`（≤1% 时）。
- 目标价 null 的卡要写明缺什么（例：`缺 peers 倍数 → 可比法 blocked`）。
字段顺序固定，方便一眼扫完。

---

## 3. 失败/降级摘要

```text
⚠️ 本轮部分失败：IBKR 行情不可用（source_error）
完成: 持仓列表（只读）| 未出买卖卡
建议: 稍后重跑，或检查 IBKR 连接
未下单
```

- 失败也要写状态与文件；不得静默退出。
- 不允许用旧行情/记忆补成"正常结果"。

---

## 4. 用户交互

- **Candidate 确认**：用户回复"确认写入 NVDA"→ 只在那一刻调用 watchlist 写工具
  （仅追加；不删不重排其他表）。
- **追问**：用户问某票 → 优先答卡上已有内容；需要新数据再采集，不重跑整轮。
- **结果回填**：用户说 watching/ignored/bought/sold/killed → 写 postmortem（contracts/memory.md）。

---

## 5. 通知与 Page

- Bot 通知（桌面/手机）由 Bot 设置决定，skill 不依赖。
- Page：仅在用户明确要求时发布（可分享团队）；routine 不发布。
- 邮件：不自动发；需要时用户在场逐封审批。

---

## 6. 文件命名

```text
out/2026-10-23-primary_babybus.md
out/2026-10-23-holdings.md
out/cards/2026-10-23/NVDA.md
out/cards/2026-10-23/XYZ.md
```

同一天重跑覆盖同名文件（状态里保留 run 记录）。

---

## 7. 语气

- 先结论后理由；短句、数字优先；中文回复。
- 不用"我认为/可能大概"堆语气；给证据和缺口。
- 不写"保证/稳赚/翻倍"；不写卖方评级话术。
- 每张卡都带"未下单"页脚。
