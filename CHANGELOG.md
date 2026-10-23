# CHANGELOG · Master pack

## 1.0.12 — 2026-10-23（NBIS 远目标降级）

- `computed_comps`：**|upside| > 50%** 一律降为 `very_wide`（cap C），不再给 `ok/B`
  （NBIS 类 target 见价的 26%、但没到 insufficient 0.2× 下限的情况）。
- config/target 合约同步；`dev/tests/test_comps.py` 增远目标案例（7 例）。

## 1.0.11 — 2026-10-23（CRWV 荒谬 target + 字段噪音）

- `computed_comps` 质量规则修正：同业 max/min >**10** 或 |upside| >200% → very_wide（C）；
  base >5× 或 <0.2× 现价 → insufficient（不可用作 target）。多 lens 按质量 + |upside| 选，
  避免选中"宽度窄但荒谬"的 EV/EBITDA。
- stdout 字段 `ticker` 改为 `symbol`（result 早已是 symbol）。
- 脚本自动清理可选 `fields_gap`：`social_x.*`、`wacc*`（并记 warnings）。
- target 触发的 TRIM/SELL 追加要求：整体 confidence ≥B；C 级只 HOLD + 复核提示
  （MOS 这种 C + RSI 9 不再自动 TRIM）。
- config 增加 comps 质量阈值与 trim/sell 置信门槛；worker prompt 同步。
- `dev/tests/test_comps.py` 增加 CRWV 类案例（应选 EV/Sales，不选荒谬 EV/EBITDA）。

## 1.0.10 — 2026-10-23（目标价重测：worker 不肯出 comps）

- 闸门修正：DCF 路线要求 `fcf_ttm > 0`（负 FCF 不再冒充 DCF 路线）。
- 新增**脚本确定性可比回退** `computed_comps`：worker 拒绝/漏掉 comps_range 时，
  脚本按 `decisions/target.md` §2.1 用 peers + 目标指标算 median/分位，附
  quality（ok/wide/very_wide/insufficient）与 confidence_cap。
- target 质量闸门：`very_wide`/`insufficient` 只能展示，不得据此 BUY 或仅因到价 TRIM/SELL。
- worker prompt：有 WACC 就用（没有也不 blocked）、holdings 不要求 social_x、
  单家 peer 不得称 median、EPS×PE 自检。
- 字段统一：脚本把 worker 的 `ticker` 归一为 `symbol` 并记 warning。
- 新增 `dev/tests/test_comps.py`（6 例）。

## 1.0.9 — 2026-10-23（5 条 routine 全量测试反馈）

- 估值闸门升级为"**路线级**"：DCF 路线（fcf+shares+net_debt+revenue）或可比路线
  （目标指标 + ≥3 家匹配 peers）至少一条完整；不再是字段拼盘。
- 可比法明确：DCF blocked 必须尝试可比；**同业分散不构成 blocked**（median + 区间，
  wide 降置信度）；只有匹配 peers 不足 3 家才允许 target=null。
- worker 硬规则：禁止使用训练知识里的财务数字（NVDA 现金幻觉的教训）；输出统一 `symbol`。
- 状态语义写死：有 target/字段缺口一律 `partial`，不能写 succeeded。
- Web 采集优先 `WebFetch`（curl 可能被 stockanalysis 等站点拦截）。
- runbook 要求每轮覆盖写全新 job，不读旧 job（避免 haochi 那类误跑旧 job）。

## 1.0.8 — 2026-10-23（Hindsight 迁移到 Cloudflare MCP）

- Hindsight 接入从 Tailscale 改为 **Cloudflare Tunnel + Caddy 令牌网关 + 远程 MCP**：
  Bot 连接器 `hindsight-sherlock-cf`，工具 `get_bank` / `recall` / `sync_retain`。
- memory 契约、capabilities、SKILL、config、README 全部更新；令牌不进技能/仓库/聊天。
- 失败处理：重试 1 次后按 `hindsight: down` 继续，标 `memory: missing`，不阻断。
- `dev/research/hindsight-connectivity.md` 重写为当前架构与排障手册；旧 Tailscale 方案弃用。

## 1.0.7 — 2026-10-23（第二轮 routine 反馈：目标价链路）

- worker 新增**估值输入闸门**：调用 DeepSeek 前校验 shares_diluted / net_debt /
  eps|revenue|ebitda / ≥3 家 peers 倍数（ETF 要发行商 NAV）；缺失则 **exit 8** 返回
  `missing[]`，不消耗 API token。Bot 按清单补采、重写 job、重跑（最多 2 次），仍不齐才
  `allow_incomplete:true` 让 worker 出 partial/null。
- 新增 `--check-job` 本地调试命令；`dev/tests/test_jobcheck.py`。
- runbook 明确：Web 必须**逐票**查股票统计页 + 3 家 peers + ETF 发行商页，并把原始值
  缓存到 `state/fundamentals/`、`state/peers/`（同日复用）。
- 摘要强制 `运行:` 行；持仓卡加"集中度"与"⚠️ 接近失效（≤1%）"提醒。
- Hindsight 诊断：服务健康（8888/health 200，三 bank 在），Bot 超时为链路/连接器问题；
  记录 `get_bank`（无 list_banks）与 Bot 侧排查命令。
- Candidate 仍只提议未持仓票（CRWV 已是持仓，不再提议）。

## 1.0.6 — 2026-10-23

- 新增 `references/runtime/config.md`：买入/加仓阈值、失效策略、trap/priced_in 闸门、
  每轮预算、Candidate 阈值、DeepSeek 模型/thinking 集中一处。
- 记录 Owner 决定：**现有持仓不设成本止损、继续持有**；仓库保持 PUBLIC。
- SKILL 加载地图增加 config.md 指针。

## 1.0.5 — 2026-10-23（第一轮真实 routine 反馈）

- 发布脚本改为 **fast-forward**：先 clone 远端、rsync、commit、push；Bot 以后 `git pull`
  即可，不再需要 `reset --hard`。
- 目标价链路增强：`fundamentals_web.peers` 改为结构化（≥3 家、倍数、来源、asof）；
  每票 Web 必须查"财务 + peers 倍数"；DCF 不可用时走可比法，peers 缺失才 null。
- 失效规则拆分：新买入用入场止损；**已持有**用结构位 + 论据 + 确认窗口，不追溯套用
  15% 止损（深亏仓不拿"回本"当理由）。
- 持仓复核新增**集中度**检查（top-2 同主题 ≥80% 必须标注）。
- Candidate 提议排除已持仓票（`position_context=neither` 才提议）。
- 记录实测连接器工具名（IBKR / X / Schwab / Tavily），Hindsight 探测重试 2 次后不阻断。
- 摘要新增 `运行:` 行，partial 必须写原因（Hindsight/估值/Web 缺失）。

## 1.0.4 — 2026-10-23（首次 Bot 实测反馈）

- 修复：`out/current.result.json` 现在写入 `analysis_source: "deepseek"`（之前只在 stdout）。
- 观察列表名纠正为实测值：`Favorites`、`ETFs`、`Assets`、`Nasdaq-QQQ`、`Candidate`；
  匹配大小写/单复数不敏感（旧文 ASSETS/Candidates 兼容）。
- `capabilities.md` 记录已观测连接器：IBKR `Interactive Brokers (IBKR)-xai`、
  X 内置、Schwab `Finance-xai`（Plaid 只读）。
- 强调目标价前提：每只分析票**必须**先做 Web 基本面/催化剂采集；没有 `fundamentals_web`
  → DCF/可比 blocked、target=null，只能观望，卡上写明原因。
- 已知：首次 job `cache.hit=0` 属正常；同一 job 再跑一次应看到命中。

## 1.0.3 — 2026-10-23

- 按 Owner 判断：DeepSeek 默认全部用 `deepseek-flash`（当前 Flash ≥ Pro）；
  `deepseek-v4-pro` 仅在显式设置 `DEEPSEEK_MODEL=deepseek-v4-pro` 时使用。

## 1.0.2 — 2026-10-23（发布准备）

- 发布到 https://github.com/Veitkwok/Master.git（公开仓库；README 安装命令用真实地址）。
- 示例数据去除真实仓位数字，改为虚构 XYZ 案例。
- 新增 `dev/publish-to-github.sh`（从 monorepo 发布 Master 内容到 GitHub）。
- `.gitignore` 增加 `.secrets/`。

## 1.0.1 — 2026-10-23（DeepSeek 调研落地）

- 模型名修正：只用 `deepseek-flash` / `deepseek-v4-pro`；`deepseek-v4.1-flash-1017`
  不是 API model ID，不能写进 `model`。
- thinking：DeepSeek 默认开启（effort=high）；routine 必须显式
  `{"thinking":{"type":"disabled"}}`，否则 reasoning token 按输出价计费。脚本已内置。
- worker 改为**固定命令**：`/usr/bin/python3 -I -B /workspace/master/skill/scripts/deepseek_analyze.py`
  + `jobs/current.json` + 紧凑 stdout；长结果写 `out/current.result.json`。
- install.sh：固定技能副本 `/workspace/master/skill`、`jobs/`、`.secrets/`（600 key 文件）。
- 审批：新增部署前预放行流程与 Custom Rules 模板；明确"审批卡住不是可 catch 异常"，
  被拦 run 记失败、下一轮补。
- 调研全文：`dev/research/deepseek-integration.md`（978 行，含官方原文/链接/成本）。

## 1.0.0 — 2026-10-23

首个 Grok Bot 版（替代 2026-10-22 Grok 迁移稿 `0.2.0`）。

### 结构
- 单入口技能 `skills/finance-master/`；20 个引擎模块降级为
  `references/engine/**/GUIDE.md`（不再作为独立 skill 注册）。
- 五层：入口 / runbooks / contracts / decisions / engine。
- 引擎 vendored（4.6.8）+ 方法核冻结 + 补丁台账。

### 新增契约
- 数据包 v2（quote / ohlcv / fundamentals / positions / watchlists / gaps）。
- 建议卡 v1：买入上限 + 目标价（base/low/high/basis）+ 卖出阶梯 + 失效条件 +
  持仓上下文 + `order_sent:false` / `schwab_trade:forbidden`。
- 置信度契约：§1.4/§1.5 原文为权威，worker 计算、Bot 只执行 ceiling。
- 状态契约：`/workspace/master/state/` 四本账 + 幂等。
- 能力探测 / 审批 / 降级矩阵。
- DeepSeek worker 契约（重活外包、JSON、失败回退 bot-inline）。

### 流程
- runbooks：KOL 主账号（3 个）、补充（3 个号合一）、持仓复核、ad-hoc。
- 排期建议：主账号 2 次/日（可 3 次）、补充 2 次/日、holdings 1 次/日（Asia/Shanghai）。

### 工具
- `install.sh` / `verify.sh` / `dev/check_pack.py` / `dev/validate_card.py` /
  `scripts/deepseek_analyze.py`（JSON、重试、降级、缓存友好）。

### 相对迁移稿修复
- 21 个嵌套 SKILL.md → 1 个入口；
- 路径根三套混用 → 相对路径 + 自动校验；
- 数据包缺估值输入 / priced_in 永远 gap → v2 补齐；
- Bot 与 DeepSeek 双跑 → 单一执行者；
- routine 无 prompt/时刻/状态 → runbooks + state；
- 引擎"原文执行"与事实不符 → 补丁台账 + hash；
- 旧工具名/旧站点/85 号名单残留 → 清理。

### 未完成 / 待实测
- Grok Bot 内 DeepSeek 调用的审批行为（`dev/research/deepseek-integration.md` 有方案）。
- IBKR watchlist 的实际工具名（按能力发现，不硬编码）。
- Schwab 连接器字段（Plaid/Finance 连接器；缺则 skip）。
