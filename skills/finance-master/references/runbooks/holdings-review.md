# Runbook · 持仓复核 routine（holdings）

> 适用：`holdings`，每个交易日 1 次（建议 08:30 +08，美股收盘后）。
> 读 IBKR + Schwab 全量持仓，并合并 `state/manual_holdings.json` 的手工券商仓（如汇丰）
> → 对照目标价/失效价/论点 → 给持有/加/减/卖。

## 0. 连接哪些数据源（别误解"不读 X"）

| 数据源 | 是否使用 | 用途 |
|--------|:---:|------|
| **IBKR** | ✅ | 持仓、账户、现价、历史、watchlist（只读） |
| **Schwab** | ✅ 只读 | 持仓、成本、交易记录 |
| **手工券商（`state/manual_holdings.json`）** | ✅ 只读 | 无连接器的仓（如汇丰）；数量/成本由用户当面告知，routine 只读不改 |
| **Web（WebFetch/Tavily）** | ✅ | 财报、新闻、催化剂、peers/基本面 |
| **Hindsight sherlock** | ✅ | 历史 case / kill criteria / target |
| **X** | ❌ 本 routine 不调用 | 持仓复核不需要社媒发现；X 读取留给 kol-primary / supplement routine，节省 X 预算 |

"不读 X"只表示**这个 routine 不调用 X 读取器**，不是不连 IBKR；如果某个持仓需要 X 情绪，
用 ad-hoc 对话或 kol routine 补，不塞进持仓复核。

---

## 1. 准备

0. **S0 第一件事**：在 `state/runs/YYYY-MM-DD.json` 追加 running 记录（先留痕再采集）；
   随后 flush `state/pending_retains.json`（Hindsight 恢复后补写失败 case）。
1. S0 能力探测（重点 IBKR、Schwab、Hindsight、state、DeepSeek）；
   并检查 `state/manual_holdings.json` 是否存在、as_of 是否超过 30 天。
2. 读 `state/runs`：今天是否已跑过 holdings？已跑过且用户未要求重跑 → 退出（幂等）。
3. 读 `state/advice`：今日 KOL routine 已出卡的票（这些仓不再重复送分析）。

---

## 2. 采集

1. IBKR：全部持仓（代码/数量/成本/现价/市值/浮盈亏%）。
   对触发分析的仓：**必须**做 Web 财务/财报日程查询，否则目标价只能 null。
2. Schwab：全部持仓 + 近期交易（只读；缺失则 skip）。
3. 手工仓：读 `state/manual_holdings.json`（文件不存在 = 本轮无手工仓，不是错误）。
   用固定命令合并 IBKR + Schwab + 手工仓（**不得**把 stdout 重定向进 `out/raw/`；
   可写 `/tmp` 或 `packs/`）：
   `/usr/bin/python3 -I -B /workspace/master/skill/scripts/merge_holdings.py`
   加上 `--manual` / `--live` / `--prices` / `--asof`（见脚本 docstring）。
   合并规则：按代码汇总；加权成本 = Σ(数量×成本)/Σ数量；市值一律用本轮 IBKR 现价
   （不得用网页行情或嘉信价顶替）。合并后的每一只（含仅手工持有的，如 AVGO）
   都算已持仓，进入轻量检查、财报窗口判定与分析名额。
   卡上按券商拆开写，例如 `MOS 35（IBKR 5+Schwab 3+HSBC 27）`；
   手工数量注明 `HSBC 数量为手工录入（as_of YYYY-MM-DD，有过期风险）`。
   某笔手工仓 as_of 距运行日超过 30 个自然日 → 缺口 `manual_holdings.stale`，
   提醒用户确认是否仍持有；**不猜、不改数量**。
   只在用户当面告知汇丰（或其他手工券商）买卖后更新该文件；routine 只读。
4. 对每个持仓：IBKR 现价 + 60–90 日线（失效价/结构用）。
5. 对每个持仓：Hindsight recall（上次 case 的 kill criteria / target / stance）。
6. watchlists 快照（只读）；不需要 X。
7. **财报日程（每个持仓都要）**：上一次与下一次财报日期 + BMO/AMC + 来源（公司 IR 页优先，
   其次 Web 日历）；同日 `state/fundamentals/` 缓存命中即可，用来做 §3.1 财报窗口判定。
   查不到日期 → 该仓 `earnings_window: unknown`，写进缺口，不猜。

---

## 3. 逐仓判断（先轻后重）

对每个仓先做**轻量检查**（无需 worker）：

```text
触发分析 = 满足任一：
  - 相对成本浮亏 ≥ 20%
  - 按市值排名前 5
  - 用户本轮点名
  - 接近失效价（≤ 失效价 × 1.03）
  - 明日/本周有财报（§3.1 preview 窗口）
  - 最近 3 个美股交易日内已出财报（§3.1 recap 窗口）
  - 记忆 case 的 kill criteria 已触发
```

- 触发 → 进入 §4 完整分析；
- 不触发 → 只列表：代码、数量、成本、现价、浮盈亏%、`状态: 正常`、`review_by`。

**全部持仓都要出现在摘要里**（列表形式），不许漏仓。

### 3.1 财报窗口判定（preview / recap，v1.0.31）

日期一律按**美东（ET）**和 NYSE 交易日算；"反应交易日" = BMO → 财报当日，
AMC/盘后 → 财报日的下一个交易日；时间不明按 AMC 处理。

```text
N       = 从反应交易日起（含当日）已收盘的 RTH 交易日数（反应日 RTH 还没收盘 → N=0）
recap   = 本季新闻稿/8-K 已发布（有来源 URL）且 N ≤ 3
preview = 未到 recap，且 下一次财报日 在今天(ET)起 7 个自然日内
none    = 其余（不加 earnings 块）
```

- 两者互斥；recap 优先。财报日已过但找不到新闻稿 → 不算 recap，按 preview 处理并在缺口写
  `earnings.release_not_found`（可能延期/日期有误），**不猜结果**。
- 例：CRWV Q3 2026-11-10 AMC → 上海 11-11 08:30（ET 11-10 19:30）的 holdings 跑 **recap**；
  价格反应只有盘后/夜盘，标 `session: post`（不是 RTH，不计入失效 3 日确认）。
- 落进 §4 的分析名额（≤3）时排序：recap > preview > 其他触发项。

---

## 4. 完整分析（≤3 个仓）

1. 按 `contracts/data-pack.md` 组包（该仓 + Web 最新事实/财报日程）。
   先读 `state/peers/YYYY-MM-DD.json`、`state/fundamentals/YYYY-MM-DD.json`
   同日缓存（命中则合并，不重复查）；未命中再查。
   **每只触发分析的仓必须逐票查 Web**：①股票统计页（shares_diluted / net_debt /
   eps 或 revenue / FCF）；②≥3 家 peers 倍数（PE/Fwd PE/EV-Sales/EV-EBITDA，带来源与 asof）；
   ③最新财报/事件。查到的值写进数据包并缓存 `state/fundamentals/`、`state/peers/`。
2. 写**全新** job 覆盖 `/workspace/master/jobs/current.json`（`mode=routine`，不复用旧 job；
   `job_id`/`asof` 用真实开始时间，不用排期时刻），执行固定命令
   `/usr/bin/python3 -I -B /workspace/master/skill/scripts/deepseek_analyze.py`。
   **exit 8 → 按 missing[] 补采 → 重跑（最多 2 次）**；仍不齐加 `allow_incomplete:true`。
   exit 2–7 或审批卡住 → bot-inline（审批卡住则本 run 记失败、下轮补）。
   **财报窗口内的仓**（§3.1）在该票 `symbols.<SYM>.earnings` 放一个块
   （格式见 `contracts/data-pack.md` §2.2）：
   - preview：`report_date`/`timing`/`quarter`/`source_url` + 一致预期 EPS/营收（带 asof 与来源）；
   - recap：新闻稿/8-K 的 actual EPS/营收 + 发布前一致预期 + 新旧指引（数字区间或带来源的方向）+
     IBKR 价格反应（`prior_close` = 财报前最后一个 RTH 收盘，`last` = IBKR 现价，写 `session`）。
   脚本看到 `earnings.phase` 才追加 earnings-preview / earnings-recap GUIDE（没有就不加载，
   不增加 token）；recap 时 fundamentals/peers 必须当轮重抓（`contracts/data-pack.md` §3）。
3. worker → CONFIDENCE_BLOCK / CHALLENGE_NODES / 估值 / trap / priced-in；
   财报仓另有 `earnings`（定性）+ 脚本 `computed_earnings`（beat/miss %、指引方向、价格反应、
   `exit_flags`）。**卡上数字一律用 `computed_earnings`**，不用 worker 文字里的数字。
   bot-inline 回退时同样只多读对应的一份 GUIDE（preview 或 recap）。
4. 按 `decisions/sell.md` §3 判定：SELL / TRIM / HOLD / ADD / REVIEW；
   已持仓的失效规则用 §1.2（结构+论据+确认窗口），**不用**新买入的 15% 止损。
5. 按 `contracts/advice-card.md` 出卡（持仓上下文、成本、浮盈亏、卖出计划）。
6. 集中度：按 `decisions/sell.md` §2.1 计算 top-2 同主题占比，≥80% 必须标注；
   市值以合并后的全书（含手工仓、IBKR 现价）为准。
7. 嘉信仓：卡上写"嘉信只读，需你手动执行"。汇丰/手工仓：卡上写
   "汇丰需你手动执行（数量为手工录入）"；**不生成任何订单或草稿**。
8. **财报只是证据，不改决策表**：stance / target / sell 仍按 `decisions/*.md` 原样判定；
   财报后 target 与 invalidation 按 `decisions/sell.md` 重算。财报仓卡上加 `earnings` 块与
   `财报:` 行（`contracts/advice-card.md`）。
9. **与 override 的关系（只提示，不处理）**：若该票有 active override，且其 `exit_now_conditions`
   里有财报类条款（如"财报 miss / 指引下调"），而 `computed_earnings.exit_flags` 命中对应项 →
   卡上 `earnings.override_exit_hit: true` 并加一行
   `⚠️ 覆盖退出条件已出现: <条款>（<数字>）· 需你在对话里决定 · 本 routine 不改判、不下单`。
   没命中写 `override_exit_hit: false`；无 override 或无财报类条款写 null。
   routine **不得**改写/撤销/续期 override，不得替用户执行退出。

---

## 5. 特殊规则

- **深亏仓**（如 XYZ −90%）：触发条件是"论点是否还成立"，不是"能不能回本"；
  论点破裂 → SELL；论点未破但仓位过大 → TRIM。
- 没有目标的仓：不编目标价；只能给"继续持有/减仓/清仓"判断 + 缺口说明。
- **失效触发**（价格 3/3 RTH 收盘或论点破裂）→ SELL，**即使 target 是 very_wide/insufficient**；
  卡上写 `触发: 失效（…）`；target 质量只约束"到目标价减仓"，不约束失效卖出。
- 今日已给过卡的同票：摘要"见今日该票卡"，不重复送 worker。
- 不因为"长期看好"而忽略失效价；不因为"跌很多"而拒绝卖出（沉没成本）。

---

## 6. 输出

1. 持仓总表（全部仓，按合并市值排序；数量列写券商拆分）；
2. 逐仓卡（触发分析者，≤3；仅手工持有的票同样按触发规则进分析，含财报窗口）；
3. 今日触发汇总：`卖出 X 个 / 减仓 Y 个 / 持有 Z 个` + 集中度提示；
4. 下次复核日（review_by）；
5. 页脚"未下单 · 嘉信只读 · 汇丰手工录入、不下单"。

每张持仓卡自检：
- 第一行 `运行: <status> · <reason>`；
- `集中度: top2 同主题 X% ⚠️`（≥80%；含手工仓市值）；
- `接近失效: 未触发` 或 `⚠️ 接近失效: 差 X%（连续 3 日中的第 N 日）`；
- 有手工腿的仓：拆分数量与加权成本来自 merge 脚本，并有 as_of 手工录入注释；
  as_of 超 30 天必须有 `manual_holdings.stale` 缺口，不得悄悄当成新数用；
- `asof` 是生成时刻，与文件 mtime 差 ≤2 分钟；
- 财报窗口内的仓：有 `财报:` 行（preview/recap）；recap 有 actual vs 预期与指引方向，
  缺数据写 `DATA_GAP`；有 active override 时写明财报类退出条件是否出现。
- 不在财报窗口的仓：**不写** `财报:` 行（不是缺口）。

---

## 7. 状态与失败

- 写 `state/runs`（`routine: holdings`）、`state/advice`（仅出卡仓）、`out/YYYY-MM-DD-holdings.md`。
- 失效确认只用 **RTH 收盘**；盘前/盘后/夜盘的跌破只提示，不计入 3 日确认。
- IBKR down → 不得编现价/市值/集中度；可列出已读到的 IBKR 之外数量与成本并注明
  "无 IBKR 现价"；不出买入/卖出卡。Schwab down → 按 IBKR + 手工仓判断并注明。
  手工文件缺失 → 只按 IBKR + Schwab（与 1.0.31 行为相同）。
- 失败不重试；下一交易日补跑。
- 更新 `state/manual_holdings.json` 只发生在用户当面告知数量变化时；
  routine 不得改写该文件。
