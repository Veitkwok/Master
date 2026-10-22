# 风险闸门（risk gates）

> 在 stance 判定之前逐道过；任何一道硬闸门不过，就不能出现买入/加仓。
> 各闸门的分析来源：trap = 引擎 `trap-detector`；priced-in = 引擎定价检查单；
> evidence = 引擎 §1.4；overlap = `contracts/book-and-overlaps.md`。

---

## 1. 闸门顺序（从硬到软）

| # | 闸门 | 硬/软 | 不过时 |
|---|------|-------|--------|
| G1 | 数据完整性（现价/持仓/分析状态） | 硬 | 观望或只列持仓 |
| G2 | trap（八信号） | 硬（橙/红） | 回避；已持有→减仓评估 |
| G3 | priced-in（是否已计入） | 硬（priced/gap） | 不新买；已持有按目标价规则 |
| G4 | 证据等级（confidence） | 硬（<B 不能买） | 观望 |
| G5 | 失效条件完整 | 硬（缺失不能买） | 观望 |
| G6 | 重叠/暴露（book） | 硬（同一暴露） | 不第二笔 |
| G7 | 流动性/冲击成本 | 软（标注） | 买但降规模/标注 |
| G8 | 仓位/现金 | 软（仅在用户说现金时写金额） | 不写金额 |

---

## 2. G2 · trap（陷阱）

- 八条信号原文：`references/engine/modules/trap-detector/references/eight-signals.md`；
  执行步骤：同目录 `GUIDE.md`。
- 来源：本轮 X 原帖 + Web 检索 + 数据包；**六个 KOL 账号不自动构成"老师人设"命中**。
- 输出：`trap_level ∈ {green, yellow, orange, red}` + 命中的信号编号与证据。
- 用法：
  - green：放行；
  - yellow：放行但必须写风险提示；
  - orange / red：**不给买点**；已持有 → 建议减仓评估（`TRIM`）。
- trap 是建议卡字段 `trap_level` 的唯一来源；worker 与 inline 冲突时取**更严**的一方。

---

## 3. G3 · priced-in（是否已定价）

- 检查单原文：`references/engine/docs/reference/priced-in-checklist.md`。
- 输出：`priced_in ∈ {not_priced, partial, priced, gap}`：
  - `not_priced`：利好/论点尚未反映在价格与预期里；
  - `partial`：部分反映（可买，但降低赔率预期）；
  - `priced`：已基本反映 → 不新买；
  - `gap`：现价与目标价逻辑脱节/关键预期数据缺失 → 不新买。
- 判定信号（≥3 条独立信号才算"priced"）：价格已走完的空间、成交/期权拥挤、
  预期已上修、同业相对强度、文件/催化剂落地情况。
- 纯 KOL 热度、X 合唱不算 priced-in 证据。

---

## 4. G4 · 证据等级

- 见 `references/contracts/confidence.md`；`BUY/ADD` 至少 **B**。
- X 单独最多 1 链 → 纯社交 ≤ C；A 需 ≥3 独立链 + 证伪完成。
- Bot 只执行 ceiling，不抬 grade。

---

## 5. G5 · 失效条件

- 必须同时有：价格失效（见 `decisions/sell.md`）与论据失效（可观测 + 窗口）。
- 缺失 → 不允许 BUY/ADD；已持有 → 只能 HOLD/WATCH + 提示补失效条件。

---

## 6. G6 · 重叠/暴露

- 规则见 `references/contracts/book-and-overlaps.md`。
- 新买的标的若与现有持仓或四张 watchlist 里的产品是同一暴露 → 不第二笔，
  在卡上写"与 X 同暴露"。
- ETF 与个股同时持有同主题 → 标注叠加风险（不强制否决，但降规模/提示）。

---

## 7. G7 · 流动性（软）

- 冷门/小盘：读 `stock-liquidity` 模块要点（ADV、价差、冲击成本）。
- 用户资金规模小（月度现金有限）时通常不是硬约束；但若单笔 > 5% ADV → 标注
  "建仓需分批、冲击成本高"。
- 不因流动性单独否决买入；写入 `key_risks`。

---

## 8. G8 · 仓位/现金（软）

- 用户**本轮没有说出现金数字** → 卡上不写金额/股数（`cash_note` 说明）。
- 用户说了现金 → 可按 `max_loss ÷ (entry − invalidation)` 给"最多可买股数"框架，
  并注明"不是必须买满"。
- 不设月度固定额度，不再使用历史 $600–1000 上限。

---

## 9. 输出（写进卡）

```text
gates:
  data: pass|fail(reason)
  trap: green|yellow|orange|red (signals: [..])
  priced_in: not_priced|partial|priced|gap
  confidence: A|B|C
  invalidation: pass|missing
  overlap: pass|same_exposure(as: QQQ)
  liquidity: ok|thin(note)
  cash: not_stated|amount
```

卡上按 `contracts/advice-card.md` 展示；摘要里只写"被哪道闸门挡住"。

---

## 10. 红线

- 不能因为"KOL 都说好"跳过 G2–G5。
- 不能用记忆里的旧 trap/priced_in 结果。
- 不能在只有 X 证据时给 B/A。
- 不能把"软闸门"当成否决理由来回避给建议；软闸门只影响规模与提示。

---

*risk gates v1 · G1–G8 · 硬闸门不过无买点*
