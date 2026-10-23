# Master v1 架构

> 目标：让 finance-master 在 Grok Bot 上**独立、稳定、省 token**地跑完整条链：
> KOL 选股 → 引擎分析（Sherlock 道 + 术）→ IBKR/Schwab 对照 → 买入/目标价/卖出卡。
> 本文件给维护者看；Bot 运行只读 `skills/finance-master/SKILL.md`。

---

## 1. 设计原则

1. **一个入口技能**：Bot 只注册 `finance-master` 一个 skill；20 个引擎模块降级为
   `references/engine/**/GUIDE.md`，避免 21 个 SKILL.md 抢路由/每轮加载。
2. **单一事实源**：方法 = 引擎；连接器/状态/审批 = runtime；判断 = decisions；
   输出 = contracts；同一规则只写一处。
3. **渐进加载**：SKILL.md ≤ 500 行；热引用 ≤150KB；引擎按需读。
4. **钱相关判断确定性化**：stance / target / sell 由判定表决定；模型只填证据。
5. **置信度是灵魂**：§1.4/§1.5 原文在引擎，worker 计算、Bot 只执行 ceiling、不重打分。
6. **数据包先行**：缺字段写 null + gaps，宁可"观望"不编数字。
7. **DeepSeek 优先做重活**：Bot 只做连接器采集与确定性裁决，省 Grok Bot usage。
8. **状态外置 + 幂等**：`/workspace/master/state/`；routines 无自动重试也能补跑。
9. **能力探测 + 降级矩阵**：任何连接器挂掉都有"还能出什么"。
10. **审批感知**：routine 只读 + 本地写；写操作留到用户在场。
11. **引擎冻结 + 补丁台账 + hash**：升级可审计，方法不被悄悄改坏。
12. **可分发可回滚**：git + install.sh + verify.sh + check_pack.py。

---

## 2. 分层

```text
skills/finance-master/
├── SKILL.md                  L0 入口：探测 → 路由 → 主链 → 红线 → 加载地图
├── references/
│   ├── runbooks/             5 条流程（KOL 主/补充、持仓复核、ad-hoc）
│   ├── runtime/              连接器能力、状态、审批、交付
│   ├── contracts/            数据包 v2、建议卡、置信度、记忆、DeepSeek、账号、账本
│   ├── decisions/            stance / target / sell / risk gates（确定性表）
│   └── engine/               冻结方法库（Sherlock + 20 模块 + 方法笔记）
└── scripts/                  DeepSeek worker、自检
```

### 数据流

```text
routine 触发
  → S0 能力探测（IBKR / X / Hindsight / Schwab / state / DeepSeek）
  → S1 状态与去重（runs / advice / mentions）
  → S2 采集数据包（IBKR + X + Web + 持仓 + watchlists + recall）
  → S3 分析：DeepSeek worker（引擎原文 + 数据包 → JSON）
              └ 失败 → Bot inline（同一引擎，标 analysis_source）
  → S4 置信度校验（ceiling 只降不升）
  → S5 决策：stance → target → sell → gates
  → S6 建议卡（买入/目标价/卖出 + 未下单）
  → S7 状态落盘
  → S8 交付（聊天摘要 + /workspace 文件）
```

---

## 3. 单一事实源矩阵

| 规则类别 | 唯一归属 |
|---|---|
| 研究方法（置信/证伪/估值/陷阱/ETF/财报/深研） | `references/engine/**` |
| 连接器/工具发现/审批/状态/交付 | `references/runtime/**` |
| 账号、X 预算、候选阈值 | `references/contracts/accounts.md` |
| 数据包字段 | `references/contracts/data-pack.md` |
| 建议卡字段与校验 | `references/contracts/advice-card.md` |
| 置信度执行 | `references/contracts/confidence.md` + 引擎 §1.4/§1.5 |
| 记忆 | `references/contracts/memory.md` |
| 买卖判断 | `references/decisions/**` |
| routine 流程 | `references/runbooks/**` |

引擎里若出现旧运行时句子（cache/lists/Scout/禁止该买/旧工具名），以入口优先，
并登记在 `engine/README.md` 补丁台账。

---

## 4. 关键契约摘要

### 数据包 v2
信封（asof/routine/connectors/gaps）+ 每票（quote/ohlcv/fundamentals_web/catalysts/
social_x/risk_flags/gaps）+ 全局 positions / watchlists。
缺 quote → 不出买卖；缺 fundamentals → target 可能 null。

### 建议卡 v1
`stance`（BUY/ADD/HOLD/TRIM/SELL/AVOID/WATCH）+ `entry_limit` + `target{base,low,high,basis,horizon}`
+ `sell_plan`（ladder / invalidation_price / invalidation_thesis / review_by）
+ `position` / `risk` / `data_gaps` / `analysis_source` + `order_sent:false` / `schwab_trade:forbidden`。

### 决策
- stance 优先级：数据缺失 > trap 橙红 > 失效 > 到目标 > 买入门槛（B、20% 上行、有失效、非已定价）。
- target：DCF 与可比都有效且分歧 ≤25% → 中值；>25% → 保守；单锚直接用；无锚 → null。
- sell：到 target.base 减 1/3、到 high 再减 1/3、失效全出；review_by = 财报或 90 天。

### 置信度
worker 按引擎 §1.4/§1.5 产出原格式；Bot 只做 ceiling（X-only ≤C、数据缺口 ≤B、
trap 橙红无买点、买入需 ≥B），返回不合格卡就降级。

### 状态
`/workspace/master/state/`：runs / mentions / advice / pending_candidates / watchlists / out。
同票同日一张卡；holdings 每日一次；失败不重试、下轮补。

### DeepSeek
worker 只吃数据包 + 固定引擎文件清单（稳定 system 前缀利于缓存），返回 JSON
（CONFIDENCE_BLOCK / CHALLENGE_NODES / 估值数字 / trap / priced_in / 失效候选），
不写 stance。Bot 出卡。不可用 → bot-inline 回退。

---

## 5. 与 Grok 迁移稿的差异（修了什么）

| 问题（迁移稿） | 本架构 |
|---|---|
| 21 个 SKILL.md 嵌套、可能被注册 | 1 个入口 + GUIDE.md 参考文件 |
| 76 处 `Master/…` + 192 处 `references/…` 断链 | 全部归一，check_pack 可校验 |
| 数据包缺估值输入 → 全卡观望 | data-pack v2 补齐 quote/ohlcv/fundamentals/positions/watchlists |
| Bot 与 DeepSeek 双跑 | Bot 采集 + worker 分析 + Bot 裁决，单一执行者 |
| routine 无 prompt/时刻/状态 | runbooks + routine-setup + state 契约 |
| 无审批/降级设计 | capabilities + approvals + 降级矩阵 |
| 无版本/同步/测试 | VERSION/CHANGELOG、补丁台账、hash、check_pack、金样/反例 |
| "库原文执行"与事实不符 | 引擎 README 登记 11 类边界补丁，方法核 hash 冻结 |

---

## 6. 上线验收

- [ ] `install.sh` + `verify.sh` + `check_pack.py` 全绿；
- [ ] Bot 能读 IBKR 持仓与四张 watchlist；
- [ ] 一条主账号 routine 端到端：X → 包 → 分析 → 卡（买入/目标价/卖出齐）→ 摘要；
- [ ] 持仓复核覆盖全部仓，0 下单；
- [ ] 反例：trap 橙红不给买、无目标价只能观望、无失效不给买、X-only ≤C；
- [ ] 同票同日不重复出卡；失败有降级摘要；
- [ ] DeepSeek 被审批拦住时能 bot-inline 回退；
- [ ] 连续一周 routine 后，用户对卡的可用性打分 ≥ 预期。

---

## 7. Owner 已确认的运行假设（2026-10-23）

| 项 | 决定 |
|----|------|
| DeepSeek 数据边界 | 接受把归一化后的持仓/成本/公开帖子发给 DeepSeek（专用 API key 只给 Bot 用） |
| DeepSeek 主路径 | Bot 本地固定命令 + `jobs/current.json` + `.secrets/deepseek.key`；不走 Tailscale |
| 备选路径 | Mac Mini 常开可做 worker；已验证 **Cloudflare Tunnel**（Hindsight 同款），shell 审批反复失败时可复用 |
| Auto Review | 保持开启；routine 审批失败 = 该 run 失败、下一轮补 |
| 模型预算 | 不设上限，优先 Flash（当前 Flash ≥ Pro）；深研才用 Pro |
| Hindsight 接入 | **Cloudflare Tunnel + Caddy 令牌网关 + 远程 MCP**（2026-10-23，Tailscale 已弃用）；Bot 用 `hindsight-sherlock-cf`，令牌只在连接器/Mac 文件，不进仓库 |
| Hindsight 写入 | 允许写 bank `sherlock`（`sync_retain`）；`hermes`/`sissyfication` 不写；失败不阻断 |
| 已有持仓止损 | **不设成本止损**，继续持有；只用结构位 + 论据 + 确认窗口（2026-10-23） |
| 仓库可见性 | 保持 PUBLIC（2026-10-23） |
| 目标价 | 6–12 月估值锚（DCF + 可比收口），90 天/财报复核 |
| 买入门槛 | 证据 ≥B + 上行 ≥20% + trap 绿/黄 + 有失效 + 非已定价 |
| 卖出 | 目标价分批 1/3 + 1/3，失效全出（默认阶梯） |

---

*Master architecture v1 · 2026-10-23*
