# 财报窗口：前瞻与复盘（earnings · preview / recap）

> **证据模块**：只写进卡，不改变 stance / target / sell / override 决策表，不自动下单。
> 触发：holdings 对每个持仓检查财报窗口；其他 routine 不强制。
> 实现：数据包 `symbols.<SYM>.earnings`（`contracts/data-pack.md` §2.2）→ worker 条件加载
> `earnings-preview`/`earnings-recap` GUIDE + `worker_earnings.md` → 脚本 `computed_earnings`
> 做确定性算术 → 卡上 `earnings` 块。

---

## 1. 窗口判定（美东 ET / NYSE 交易日）

- `反应交易日` = BMO → 财报当日；AMC/盘后 → 财报日的下一个交易日；时间不明按 AMC。
- `N` = 从反应交易日起（含当日）**已收盘的 RTH 交易日数**（反应日 RTH 未收盘 → N=0）。
- `recap` = 本季新闻稿/8-K 已发布（有来源 URL）且 `N ≤ 3`；
- `preview` = 未到 recap，且下一次财报日在今天(ET)起 **7 个自然日内**；
- `none` = 其余，不写 earnings 块。
- recap 优先；财报日已过但找不到新闻稿 → 按 preview + 缺口，**不猜结果**。

## 2. 超预期判定（带容差）

```yaml
earnings_surprise_tolerance:
  eps_pct: 1.0        # ±1%
  revenue_pct: 0.5    # ±0.5%
```

- `beat`：variance > +tolerance；
- `miss`：variance < −tolerance（**material miss**，`exit_flags.*_miss=true`）；
- `inline`：在 ±tolerance 内；
- `technical_miss`：actual < consensus 但仍在容差内（label=inline，`technical_miss=true`，
  **不构成退出条件**）。
- 卡上写具体 variance；数字来自 `computed_earnings`，不手算。

## 3. 数据与来源

- 实际值来自公司新闻稿/8-K/IR；一致预期至少一个来源（consensus）。
- 每项带 `source_url` 与 `asof`；缺则 `null` + `fields_gap`，不编数字。
- EPS 标口径（adj/GAAP）；指引方向：`raised|maintained|lowered|none`；
  数字区间可由脚本算中点比较，否则用包内带来源的方向。
- 价格反应来自 IBKR：`prior_close` = 财报前最后一个 RTH 收盘，`last` = 当前价，
  `session: post|regular|pre|overnight`；**盘后/夜盘不计入失效 3 日确认**。

## 4. 与覆盖/失效的关系

- 只有 **material miss** 或 **指引 lowered** 才可能写
  「⚠️ 覆盖退出条件已出现」；即使命中，routine 也只提示，**不改判、不下单**。
- beat + 上调不自动撤销已确认的价格失效；覆盖是否续期/执行由用户决定。
- 财报后 target / invalidation 按引擎重算，不沿用旧值。

## 5. 卡面格式

```text
财报: 复盘 Q3（11-10 盘后）EPS -$0.20 vs 预期 -$0.25（+20.0%，beat）| 营收 $1.30B vs $1.40B（−7.1%，miss）| 指引 下调 | 盘后 −10.0%（IBKR）
⚠️ 覆盖退出条件已出现: 指引下调 · 需你在对话里决定 · 本 routine 不改判、不下单
```

preview：

```text
财报: 前瞻 Q3（11-14 盘前）一致预期 EPS $1.10 / 营收 DATA_GAP · 看点: …
```
