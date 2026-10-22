# CHANGELOG · Master pack

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
