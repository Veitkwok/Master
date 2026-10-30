# Routine 配置（Grok Bot · 一次性设置）

> **2026-10-30 起推荐 4 条 routine**（原 5 条布局在平台出现连续中断后弃用）。
> 原因：Grok Bot 的 routine 并发/自动化限流会让靠得太近的 run 在启动阶段被平台标 failed；
> 把 3 个主号合并成 1 条顺序执行的 routine，可显著减少并发。
> 时区：Settings → Bot → Timezone = `Asia/Shanghai`。

---

## 1. 先决条件

- [ ] 已跑过 `bash install.sh`（技能库在 `~/agent-data/workflows/finance-master`；
      状态目录在 `/workspace/master/state`）。
- [ ] Bot 已能读 IBKR 持仓 + 四张 watchlist（在对话里试一次）。
- [ ] DeepSeek key 已放（`.secrets/deepseek.key` 或环境变量）。
- [ ] Approvals：Auto Review；下单/草稿/watchlist 写/邮件 = Ask first；
      固定 worker 命令已预放行（见 §2）。
- [ ] **旧的 5 条 routine 先 Disable/删除**，避免和新的 4 条抢并发。

---

## 2. 预放行 DeepSeek 固定命令（部署前必做）

1. 在有人在场的对话里手动跑一次：
   `/usr/bin/python3 -I -B /workspace/master/skill/scripts/deepseek_analyze.py --selftest`
2. 再手动跑一次真实 job（先用 Test job）；出现审批 → **Always allow**。
3. Settings → General → Auto-review → Custom Rules：添加 Allow 规则
   （模板在技能内 `references/runtime/approvals.md` §2.1）。
4. 连续跑 2–3 次确认不再弹卡；然后才启用 routine。
5. 无人值守审批约 10 分钟过期且动作不执行；被拦 = 该 run 失败，下一轮补。

### 2.1 routine 里不要重定向 stdout

- 固定命令直接运行即可；**不要**写 `> /workspace/master/out/raw/...` 之类的重定向。
  raw 由 `deepseek_analyze.py` 原子写入 `.worker.stdout.json`。
- `job_id` / `asof` 用 S0 真实开始时间，不要用排期时刻。
- `job_id` 推荐 `YYYYMMDD-<routine>-HHMM`（脚本也容忍 `YYYYMMDD-HHMM-<routine>`）。

---

## 3. 推荐的 4 条 routine

| # | routine | 时间（Asia/Shanghai） | 内容 |
|---|---------|----------------------|------|
| 1 | `kol-primary` | **07:30** | 顺序跑 3 个主号（babybus → haochi → balder） |
| 2 | `supplement` | **08:10** | 一次性读 3 个补充号 |
| 3 | `holdings` | **08:30** | 不读 X，IBKR + Schwab 全持仓复核 |
| 4 | `daily-report` | **09:10** | 日检：终态记录/缺口/卡数/raw/FAIL 汇总 |

间隔 ≥40 分钟；如果平台稳定后再考虑把主号拆回 3 条。

### 3.1 kol-primary（合并主号）

- Schedule：`每天 07:30`
- Prompt：

```text
使用 finance-master 技能，依次执行 references/runbooks/kol-primary.md 三次：
1) routine_id=primary_babybus, account=BabybusFL
2) routine_id=primary_haochi, account=haochihaochiaaa
3) routine_id=primary_balder, account=Balder13946731（不打开 Balder 网站，只读 X）

每次都必须独立写 state/runs、jobs/current.json、out/raw、摘要与卡片；三次之间不要跳过；
全部完成后输出一份合并摘要（每次的状态/耗时/卡数/target/可操作票/错误）。
只读连接器；不写 watchlist、不下单、不发邮件。
```

### 3.2 supplement

- Schedule：`每天 08:10`
- Prompt：

```text
使用 finance-master 技能，执行 references/runbooks/kol-supplement.md。
参数：routine_id=supplement, accounts=aleabitoreddit,jiaao_wu,KotlinerBTC。
只读 X 与 IBKR；不写 watchlist、不下单；按摘要格式输出。
```

### 3.3 holdings

- Schedule：`每天 08:30`
- Prompt：

```text
使用 finance-master 技能，执行 references/runbooks/holdings-review.md。
参数：routine_id=holdings。
连接 IBKR（持仓/行情/watchlist 只读）+ Schwab（只读）+ Web（财报/新闻/基本面）+ Hindsight；
持仓复核不需要社媒发现，因此不调用 X 读取器（不是不连 IBKR）。
只读；不写 watchlist、不下单；嘉信只读。
```

### 3.4 daily-report（日检）

- Schedule：`每天 09:10`
- Prompt：

```text
使用 finance-master 技能做当日日检（只读，不重复分析）：
1) 读取 state/runs/今天 的记录；跳过 run_tag=manual 的手动测试；
2) 3 条日常 routine（kol-primary 里 3 个主号、supplement、holdings）都要有终态记录；
   缺记录 → failed(no_record)；仍为 running 且 started 超过 2 小时 → failed(interrupted)；
3) 检查 out/raw 的 *.worker.stdout.json 都是合法 JSON；
4) 检查卡数 = sync_retain 数、卡片有 运行:/证据/目标质量/集中度/接近失效；
5) 任一项不过 → 标题写 FAIL 并列出；全部通过 → PASS；
6) 输出到 /workspace/master/out/YYYY-MM-DD-daily-report.md。
不要写 watchlist、不下单、不发邮件。
```

---

## 4. 平台中断的处理

- 平台把 run 标 failed 时，Bot 侧可能只留下 `status:"running"` 的起跑记录；
  下一轮/日检必须把它标 `failed(interrupted)`，**不允许**当成成功。
- 同一个 routine 连续 2 天被中断：
  1. 先在 Grok Bot 的 **run history** 看平台给的失败原因（并发/限流/超时/配额）；
  2. 把排期再拉开 10–20 分钟，或把该 routine 合并进相邻 run；
  3. 仍不行就把该 routine 改成手动 Test，观察一段时间。
- 失败后不需要当天补跑：下一次正常运行会按"距上次成功"窗口自动补数据；
  想立刻补就手动 Test 该 routine。

---

## 5. 出问题先看哪里

| 现象 | 先查 |
|------|------|
| routine 没输出/被中断 | Bot run history；`state/runs` 是否为 failed(interrupted)/running |
| 卡全是观望 | target 是否因缺 fundamentals/peers 被 blocked；confidence 是否 C |
| 没调用 DeepSeek | 审批拦截/密钥缺失；摘要 `analysis_source` |
| raw 文件坏 | 只认 `*.worker.stdout.json`；routine 不得重定向进 out/raw |
| Candidate 状态不同步 | 写入成功后 pending_candidates 的 confirmed/written_at |
