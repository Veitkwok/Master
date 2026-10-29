# Runbook · KOL 主账号 routine

> 适用：`primary_babybus` / `primary_haochi` / `primary_balder`（一次只读一个主账号）。
> routine prompt 参数：`routine_id`、`account`（handle）、可选 `window_override`。
> 目标：读该账号最新帖子 → 选票 → 分析 → 对照持仓 → 出买单/目标价/卖出卡。

---

## 1. 准备（S0–S1）

0. **S0 第一件事**：在 `state/runs/YYYY-MM-DD.json` 追加
   `{routine, account, job_id, started, status:"running"}`（先留痕再采集）。
1. 按 `SKILL.md` §2 做能力探测（IBKR / X / Hindsight / Schwab / state / DeepSeek）。
2. 读 `state/runs/YYYY-MM-DD.json` 与 `state/advice/`：
   - `since = 该 routine 上次成功时间`，上限 14 天；无记录则用 7 天。
   - 今日已出卡的票记下来（本轮不重复出卡）。
3. 读 `state/mentions.jsonl` 最近 14 天（候选频率用）。

失败：X down → 输出"本轮无 X 数据"，写状态，退出（不要编帖子）。
IBKR down → 继续采集 X 与 Web，但本轮**不出买入/卖出卡**（只列观察）。

---

## 2. 读 X（按 contracts/accounts.md 预算）

1. 读 `@<account>` 时间线（`from:<account>` + `since:`），**1 次**。
2. 正文截断且可见部分含美股代码/明确多空句 → 补读 1 次主帖（最多 2 次）。
3. 按 `references/engine/modules/x-advanced-research/GUIDE.md` 抽取：
   - 代码/公司名、作者原句、链接、时间、conviction_hint、paid_or_promo；
   - 非美股丢弃（不中止整轮）；回复/转推无评论丢弃；每账号只留最新 8 条原文。
4. 把本轮帖子写入 `state/mentions.jsonl`（新增，去重）。

---

## 3. 选票与组数据包

1. 候选排序：机制/数字/时间窗 > 多账号提到 > 仅代码。
2. 取前 **≤3** 只进入分析（用户点名优先）；其余写"观察"（代码 + 原句）。
3. 对每只分析票，按 `contracts/data-pack.md` 组包：
   - IBKR：resolve 合约 → 现价/快照 → 60–90 日线（MA/RSI）→ 四张 watchlist（只读）；
   - 先读 `state/peers/YYYY-MM-DD.json`、`state/fundamentals/YYYY-MM-DD.json`
     同日缓存：命中就直接合并进数据包，不重复查；未命中再 Web 查。
   - Web：**逐票单独查**（不要把三只票合并成一次查询），每票 2–3 次
     （stockanalysis/发行商页优先用 `WebFetch`；curl 可能被站点拦截）：
     ①股票统计页：`shares_diluted`、`net_debt`、`eps_ttm`/`revenue_ttm`、FCF；
     ②**≥3 家 peers 的估值倍数**（PE/Fwd PE/EV-Sales/EV-EBITDA，带来源与 asof）；
     ③ETF 加发行商页（NAV/折溢价/费率/持仓）。查到的原始值写进数据包，并缓存到
     `state/fundamentals/`、`state/peers/`（同日可复用）。
     - 没有 `shares_diluted`/`net_debt`/peers → 脚本 exit 8；补采后再跑（最多 2 次）；
     - 不能用"感觉贵/便宜"凑目标价，不能编倍数。
   - X：本轮该账号帖子（≤8 条，含链接）；
   - Hindsight：按 ticker recall；
   - positions：IBKR 全量 + Schwab（若可用）。
4. 每只票记录 `source: primary`、`kol_evidence`（原句 + 链接）。

---

## 4. 分析（fixed command · worker 优先）

1. 按 `contracts/deepseek.md` 组装**全新** job：`job_id` / `mode=routine` / `asof` /
   `pack=数据包`，覆盖写 `/workspace/master/jobs/current.json`（不复用旧 job 文件）。
   `job_id` 与 `asof` 都用**本轮真实开始时间**（S0 取本机时钟），不得用排期时刻。
2. 执行唯一固定命令（逐字）：
   `/usr/bin/python3 -I -B /workspace/master/skill/scripts/deepseek_analyze.py`
3. **exit 8 = 估值输入不齐**：读 stdout `missing[]`，按字段补 Web 采集，更新 job，重跑
   （同一命令，最多 2 次）。仍不齐 → job 加 `"allow_incomplete": true` 重跑一次。
   exit 0 → 进第 4 步；exit 2–7 → 本 run `analysis_source=bot-inline`，读引擎 inline
   完成分析并把错误类写进 state。
4. **审批卡住 ≠ 脚本失败**：命令可能不会执行，run 会因审批过期而失败——
   写 `deepseek_status=blocked` 并结束本轮，**下一轮补跑**（不要在同一 run 里等）。
5. 校验：`contracts/confidence.md` §5 的拒绝清单。

---

## 5. 决策与出卡

1. 按 `decisions/stance.md` 逐票判定（优先级命中即停）。
2. `decisions/target.md` 收口目标价与 `entry_limit`；`decisions/sell.md` 给卖出计划与失效。
3. 按 `contracts/advice-card.md` 生成卡；**买入、目标价、卖出三样齐全**或明确缺失。
4. 同票今日已出卡且无新证据 → 摘要"见今日该票卡"。

---

## 6. 落状态与交付

1. 写 `state/runs/YYYY-MM-DD.json`（追加本 run）、`state/advice/YYYY-MM.jsonl`（每卡一行）、
   `state/watchlists/YYYY-MM-DD.json`（快照）。
2. Candidate：满足 `contracts/accounts.md` 阈值、且该票 `position_context=neither`
   （不提议已持仓）→ 写 `state/pending_candidates.json` 并**提议**；
   异常：列表不存在 → 只提示，不创建。
3. 写 `out/YYYY-MM-DD-<routine>.md`、`out/cards/YYYY-MM-DD/<SYM>.md`。
4. 按 `runtime/delivery.md` 输出聊天摘要（含"未下单"页脚）。

---

## 7. 边界与失败

- routine 内**不写 watchlist、不下单、不发邮件**。
- 只分析该账号本轮提到的票；不主动扫其他账号（补充账号由 supplement routine 负责）。
- 同一交易日里，该账号若无新帖 → 输出"无新增"，不重复分析旧票。
- 失败写 `status: failed` + errors；下一轮按 `next_catchup_from` 补跑。

---

## 8. 完成标准（自检）

- [ ] 帖子都有链接/时间/原句；
- [ ] 每只卡票有 CONFIDENCE_BLOCK + CHALLENGE_NODES；
- [ ] 买入卡有 entry_limit、target、invalidation、confidence ≥ B；
- [ ] 卖出/减仓卡有触发原因；
- [ ] 摘要与**每张卡**第一行都有 `运行: <status> · <partial 原因>`；
- [ ] 卡片 `asof` 是生成时刻、与文件 mtime 差 ≤2 分钟（不是 run started）；
- [ ] 每张卡目标价有值，或写明缺什么导致 null；
- [ ] 状态三处已写；摘要含"未下单"；
- [ ] 没有写 watchlist / 没有编数据。
