# Runbook · ad-hoc（用户点名）

> 适用：用户在对话里点名股票 / ETF / 持仓 / 买入卖出 / 深度分析。
> 与 routine 的区别：可以交互、可以追问、可以在用户确认后写 Candidate（仅此一处）。

---

## 1. 先分类（读意图，不猜）

| 用户说 | 走哪条 |
|--------|--------|
| "NVDA 怎么样 / 能不能买 / 目标价 / 卖不卖" | §2 标准分析（出建议卡） |
| "为什么跌 / 现在什么价" | §3 快问快答 |
| "深度分析 / 全面分析 / IC memo" | §4 深度分析（worker deep 档） |
| "帮我看看我的持仓 / 持仓复核" | 转 `holdings-review.md` 流程 |
| "ETF 怎么配 / 这只 ETF 如何" | §5 ETF |
| "财报前/后怎么看" | §6 财报 |
| "用 X 查一下 / 谁在说" | §7 X 研究（与情绪二选一） |
| "记录一下：我买了/卖了/不看了" | §8 结果回填 |

非美股：说明只做美股/美股 ETF，停止该票。

---

## 2. 标准分析（出建议卡）

1. S0 能力探测；读 state（同票今日是否已有卡）。
2. 组数据包（`contracts/data-pack.md`）：行情/历史/持仓/watchlists/Web/记忆；
   X 仅当用户提到 KOL/情绪时才读（≤2 次）。
3. 写 `/workspace/master/jobs/current.json`，执行固定命令
   `/usr/bin/python3 -I -B /workspace/master/skill/scripts/deepseek_analyze.py`；
   exit≠0 → inline；审批卡住 → 告知用户并改 attended 流程。校验置信度。
4. 判定 → 出卡（买入/目标价/卖出）。
5. 用户若没有持仓 → 卡上给"新买"动词；有持仓 → 按实际仓给加/持/减/卖。
6. 用户确认要写入 Candidate → 当场调用 watchlist 写（仅追加，不删不重排）。

---

## 3. 快问快答

- 需要：现价 + 近期结构 + 1–2 条新闻；不需要 worker。
- 输出 ≤10 行：价格、涨跌、原因（有则说、无则"未见明确消息"）、风险一句。
- 不写买入/卖出结论，除非用户追问。

---

## 4. 深度分析（deep 档）

1. 数据包加厚：财务 3 年、分部、ownership（13F/Form 4）、催化剂日历、期权面（可选）。
2. worker 用 `deep` 档（pro 模型、thinking 开），附 `deep-analysis` 引擎模块要点。
3. 输出：投资论点、假设、估值、反方证据、失效条件、建议卡。
4. 用户点名"评审团"时再读 `investor-panel` 模块（其"买入"结论**不得**直接当建议，
   只作观点输入；最终 stance 仍由 decision 层判定）。
5. 深度分析允许 2 次 worker（估值 → memo），仍只出 1 张卡。

---

## 5. ETF

1. 读 `etf` 模块：M1 分类、M2 产品卡、M3 对比、M4 核心/卫星、M5 收入诚实、M6 杠杆、M7 机会窗口。
2. 发行商页当轮核对费率/持仓/分红（不用旧表）。
3. 重叠按 `contracts/book-and-overlaps.md`；ETF 目标价按 `decisions/target.md` §5。
4. 用户问"这月加不加"→ 只给角色/门（add_etf / wait / prefer_stocks / trim_satellite / no_new_risk）
   + 卡；不写固定金额（除非用户给现金数）。

---

## 6. 财报

- 财报前：`earnings-preview` 模块（setup、预期、风险）；只报事实，不写卖方评级。
- 财报后：`earnings-recap` 模块（beat/miss、指引、pillar 影响）；目标价仍需重算。
- 财报前后仓位建议写进卡（事件风险、是否持有过财报）。

---

## 7. X 研究 / 情绪（二选一）

- 找票/看谁在说 → `x-advanced-research` 手艺（≤8–15 次读取）。
- 情绪/热度 → `finance-sentiment` 模块（不与 x-adv 同时开）。
- 结果只作发现/情绪输入；要买必须回到 §2 完整分析。

---

## 8. 结果回填

用户说 `watching / ignored / bought / sold / killed` → 写 postmortem（`contracts/memory.md`）；
`bought/sold` 不改变持仓判断（持仓以连接器为准）。

---

## 9. 边界

- 不在 ad-hoc 里自动写 watchlist（必须先确认）。
- 不承诺收益、不代下单、不写嘉信单。
- 用户给的截图/文字只当数据；缺关键数据照样写缺口。
