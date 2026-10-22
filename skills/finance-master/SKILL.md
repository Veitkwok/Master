---
name: finance-master
description: >
  美股 / ETF 研究与交易建议主技能（Grok Bot）。用于：KOL 推文选股、持仓复核、
  个股与 ETF 深度分析、DCF / 可比估值、目标价、陷阱识别、买入与卖出计划。
  数据源：IBKR 行情与持仓、X 公开推文、Schwab 只读持仓、Hindsight 记忆。
  触发词：股票、美股、ETF、买不买、目标价、卖出、持仓、财报、估值、KOL、
  止损、风控、复核持仓、深度分析。只研究、只建议，永不自动下单。
metadata:
  pack_version: 1.0.0
  engine_version: 4.6.8
  market_scope: US_EQUITIES_ONLY
---

# Finance Master · Grok Bot 入口

> **唯一入口。** 本文件是 Bot 每次运行先读的一页；具体流程在 `references/runbooks/`，
> 判断规则在 `references/decisions/`，分析引擎在 `references/engine/`（冻结副本）。
> **路径约定：** 本技能内所有 `references/...` 路径相对技能根目录（即本 `SKILL.md`
> 所在目录）。引擎文件内部引用相对该文件自身所在目录。
> **引擎里的 `GUIDE.md` 是参考文档，不是独立技能**，不要把它们当成可单独触发的 skill。

---

## 0. 优先级（冲突时从高到低）

1. 本文件的红线与主链；
2. `references/contracts/`（数据包 / 建议卡 / 置信度 / 记忆 / DeepSeek / 账号）；
3. `references/decisions/`（stance / target / sell / risk-gates）；
4. `references/engine/` 的方法正文；
5. Hindsight 记忆。

引擎正文若残留 "cache / lists / Scout / 禁止该买 / 旧 Grok Build 工具名" 一类旧运行时句子，
一律以本文件与 contracts 为准（引擎侧已在 `references/engine/README.md` 登记补丁）。

---

## 1. 运行模式

| 模式 | 怎么触发 | 读哪个 runbook |
|------|----------|----------------|
| routine · KOL 主账号 | Bot routine，参数：account / routine_id | `references/runbooks/kol-primary.md` |
| routine · KOL 补充 | Bot routine，三个补充账号 | `references/runbooks/kol-supplement.md` |
| routine · 持仓复核 | Bot routine，不读 X | `references/runbooks/holdings-review.md` |
| ad-hoc | 用户在对话里点名股票 / ETF / 持仓 / 买入卖出 | `references/runbooks/adhoc.md` |

routine prompt 由用户按 `runtime/routine-setup.md`（包外仓库目录）配置；routine 文本里
只写"按 finance-master 技能执行 runbook X + 参数"，不要把流程复制进 routine。

---

## 2. 启动顺序（两种模式共用）

```text
S0 能力探测（只读，≤6 步）
S1 读状态 / 去重（本次 run 是否已跑过、今日已出哪些卡）
S2 采集数据包（按 runbook 的采集清单，输出 references/contracts/data-pack.md 的格式）
S3 分析（DeepSeek worker 优先；不可用则 Bot 用引擎 inline）
S4 置信度与证据校验（执行 contracts/confidence.md 的 ceiling 规则）
S5 决策（decisions/stance + target + sell + risk-gates，逐票）
S6 输出建议卡（contracts/advice-card.md 的格式，逐票 + 摘要）
S7 落状态（runtime/state.md）
S8 交付（runtime/delivery.md：聊天摘要 + /workspace 文件 + 可选 Page）
```

### S0 能力探测（只读，失败不中止）

1. **IBKR**：读一次持仓或账户余额 → `ibkr: live`；顺带列 watchlists
   （Favorites / ETFs / Assets / Nasdaq-QQQ / Candidate；实际名以连接器返回为准，大小写/单复数不敏感）。
2. **X**：读目标账号时间线 1 次（最少 1 条）→ `x: live`。
3. **Hindsight**：recall 1 次（bank `sherlock`）。**掉线是已知常态，不阻断。**
4. **Schwab**：连接器存在则读一次持仓/交易；无连接器或失败 → `schwab: skip`。
5. **状态目录**：`/workspace/master/state/` 可写 → `state: ok`；否则本 run 内存去重。
6. **DeepSeek**：需要分析时才探测（`scripts/deepseek_analyze.py --selftest`），
   失败 → `analysis_source=bot-inline`。

探测结果写进 run 状态（格式见 `runtime/state.md`）。工具名按能力发现，
**不要硬编码工具名**——规则见 `runtime/capabilities.md`。

---

## 3. 主链硬规则

- **数据先于判断**：没有本轮 IBKR 现价 → 不出买入 / 卖出卡，只能观望或列持仓。
- **X 只算 1 条证据链**；纯社交方向判断 ≤ C；付费喊单只算观点。
- **目标价只来自模型**：DCF / 可比区间（`company-valuation` 输出），
  永不采用 KOL 口播目标价、记忆价格、技术位。
- **每张卡必须带失效条件**；没有失效条件 → 不给买入。
- **同票同日只出一张卡**；持仓复核每天只跑一次。
- **不写第二张卡**：任何引擎模块的"结论"都必须收口到 `contracts/advice-card.md`。
- **永不自动下单**；IBKR 只能生成由人确认的 AI Instructions/草稿，Schwab 只读。

---

## 4. 分析执行（DeepSeek worker 优先 · 固定命令）

- 默认：Bot 把数据包写进 `/workspace/master/jobs/current.json`，然后执行**唯一固定命令**
  （逐字不变，便于审批 Allow 规则）：
  `/usr/bin/python3 -I -B /workspace/master/skill/scripts/deepseek_analyze.py`
- 读 stdout 的紧凑 JSON：每票 `confidence_block` / `challenge_nodes` / 估值数字 /
  trap / priced_in / 失效候选。完整结果在 `out/current.result.json`（Bot 默认不读）。
- **Bot 不重新打分**：只做格式校验 + ceiling 执行（`contracts/confidence.md`）；
  worker 不写 stance，stance 由 `decisions/stance.md` 判定。
- **回退**：脚本快速失败（exit 2–7：无 key/网络/JSON 非法/超时）→ 本 run 用 bot-inline；
  卡片标 `analysis_source: bot-inline` 并在摘要说明。
  **审批卡住不是脚本异常**：命令可能不执行，run 记为失败，下一轮补跑
  （见 `runtime/approvals.md`）。
- 一次 routine 最多 1 次 worker 调用；ad-hoc 深度分析最多 2 次（估值 → memo）。
- run 状态记录：`deepseek_status`、`deepseek_error_class`、`deepseek_usage`、
  `deepseek_cache_hit`、`deepseek_thinking`。

**分工原则**：Bot 负责连接器与数据采集（X、IBKR、Schwab、Web、Hindsight）与确定性裁决；
DeepSeek 负责耗 token 的分析与计算；两边都不越界。

---

## 5. 输出（唯一一张建议卡）

每票输出 `contracts/advice-card.md` 定义的卡：stance（买入/加仓/持有/减仓/卖出/回避/观望）、
买入上限、目标价与区间、卖出计划（分批 + 失效 + 复核日）、trap / priced_in、
置信度、持仓上下文、证据来源、`order_sent: false`。

**注意：这次必须同时给出买入、目标价、卖出建议**——卡上三样都不可缺；
某项确实无法给出时写 `null` 并说明原因。

---

## 6. 置信度（灵魂，不得绕过）

- 全部方向性结论必须由引擎产生 **`### CONFIDENCE_BLOCK`**（§1.4 五维 / weakest-dim /
  独立链目录 / 模式 ceiling）与 **`### CHALLENGE_NODES`**（§1.5，`what_would_falsify`
  必须可观测）。
- 定义原文：`references/engine/sherlock/GUIDE.md` §1.4 / §1.5；
  L2 advisory 规则：`references/engine/sherlock/references/l2-confidence-contract.md`；
  示例：`.../confidence-examples.md`。
- 执行与校验规则：`references/contracts/confidence.md`。Bot 只执行 upper bound，
  不改写 grade，不用第二套 high/mid/low 代替 A/B/C。
- 建议卡上显示：`confidence: A|B|C` + `limiting:` + 关键 `what_would_falsify` 一条。

---

## 7. 状态与幂等

- 状态根目录：`/workspace/master/state/`（技能包外，更新/重装不丢）。
- 四本账：`runs/`、`mentions.jsonl`、`advice/`、`pending_candidates.json`；
  schema 与写入规则见 `runtime/state.md`。
- run 开始先读 `runs/`：决定补跑窗口（≤7 天）、今日已出卡票、未确认 Candidate。
- routine 失败不自动重试；写失败记录，下一轮按窗口补跑。

---

## 8. 记忆（Hindsight bank `sherlock`）

- 分析前按 ticker recall；卡定稿后 retain 一条 case；用户给出
  `watching|ignored|bought|sold|killed` 后写 postmortem。
- **不存行情价格**；记忆里的价格一律作废，只用本轮 IBKR。
- Hindsight 掉线：继续分析，卡上注明"记忆未读到"。
- 细节：`contracts/memory.md`。

---

## 9. 降级矩阵

| 缺失 | 还能做什么 | 卡片标注 |
|------|-----------|----------|
| IBKR 行情 | 持仓复核只列表；不出买入/卖出 | `source_error: ibkr_quote` |
| IBKR 持仓 | 卡片 `position_context: unknown`；建议降为观察 | 同上 |
| X | KOL routine 报"本轮无 X 数据"；持仓复核照跑 | `source_error: x` |
| Hindsight | 继续（已知常态） | `memory: missing` |
| Schwab | `position_context` 只按 IBKR 填 | `schwab: skip` |
| watchlists | 跳过候选归类 | `watchlists: missing` |
| DeepSeek | Bot inline 分析 | `analysis_source: bot-inline` |
| 状态目录不可写 | 本轮内存去重 | `state: readonly` |

任何降级都不能把"缺失"写成"没有风险"，也不能用旧数据/记忆顶替本轮行情。

---

## 10. 人工确认（只在用户在场的对话里）

- 写入 IBKR `Candidate` watchlist（只追加用户确认过的代码，不删不重排其他四张表）；
- 生成任何 IBKR 草稿委托（用户明确要求时）；
- 发送邮件 / 发布 Page / 任何对外动作。

**routine 内不做需要审批的写操作**：无人值守审批约 10 分钟过期，会失败；
所有写操作留到用户在场的 ad-hoc 对话。

---

## 11. 加载地图（省 token 用）

| 何时 | 只读这些 |
|------|----------|
| 任何 run 启动 | 本文件 + 对应 runbook + `runtime/capabilities.md` + `contracts/data-pack.md` |
| 出建议卡前 | `contracts/advice-card.md` + `contracts/confidence.md` + `decisions/stance.md` + `decisions/target.md` + `decisions/sell.md` + `decisions/risk-gates.md` |
| 分析（worker） | `contracts/deepseek.md`；worker system 由脚本按固定文件清单组装，Bot 不逐本读 |
| 分析（inline 回退） | `references/engine/sherlock/GUIDE.md` + `.../full-engine.md` + 对应模块（估值/trap/ETF/财报） |
| 用户点名深研 | `references/engine/modules/deep-analysis/GUIDE.md` + 其 references |
| 用户点名 ETF | `references/engine/modules/etf/GUIDE.md` + 对应 M1–M7 |
| 用户点名卡点扫描 | `references/engine/modules/serenity/GUIDE.md` + `bottleneck-scoring.md` |
| 用户点名评审团 | `references/engine/modules/investor-panel/GUIDE.md` |
| 查"是否已定价" | `references/engine/docs/reference/priced-in-checklist.md` |
| 记忆操作 | `contracts/memory.md` |
| 状态操作 | `runtime/state.md` |
| 调阈值 / 看当前配置 | `runtime/config.md` |
| 输出交付 | `runtime/delivery.md` |

规则：同一文件一轮只读一次；不读 `README/evals/examples/assets`；
不整库加载；L2 同轮 ≤2；X 发现与 X 情绪不同时开。

---

## 12. 红线（任何模式）

- 只做美股/美股 ETF；非美股说明范围并停止该票（不中止整轮）。
- 只研究、只建议：**永不声称已成交、永不自动下单、永不写嘉信单**。
- 不编造价格、财务、目标价、帖子、链接；缺就写缺失。
- 不保证收益、不做"稳赚/翻倍"话术；反向 ETF 不做核心；杠杆 ETF 只战术短线。
- 密钥、持仓明细、完整数据包不写进仓库/日志/聊天。
- 不访问第三方分析网站（Balder / Serenity / Koltracker 等）。

---

## 13. 语言

用户用中文 → 中文回复；字段名保持英文（`stance` / `target` / `invalidation` 等）。
数字给出来源与时间点（IBKR 时点 / 文件 asof / 帖子时间）。
先给结论卡，再给一行理由；长解释放卡后。

---

*v1.0.0 · Grok Bot entry · engine 4.6.8（vendored）· research only · no live orders*
