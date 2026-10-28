# Routine 配置（Grok Bot · 一次性设置）

> 在 Bot 的 Routines 里建 5 类 routine。**Prompt 很短**，流程都在技能里。
> 时区：Settings → Bot → Timezone = `Asia/Shanghai`。
> 每个 routine 可以一天触发一次；要一天两轮就复制一个、改时间（Bot routines ≤50）。

---

## 1. 先决条件

- [ ] 已跑过 `bash install.sh`（技能库在 `~/agent-data/workflows/finance-master`；
      状态目录在 `/workspace/master/state`）。
- [ ] Bot 已能读 IBKR 持仓 + 四张 watchlist（在对话里试一次）。
- [ ] Secrets 里有 `DEEPSEEK_API_KEY`（可选；缺失则回退 bot-inline）。
- [ ] Approvals：Auto Review；下单/草稿/watchlist 写/邮件 = Ask first。

---

## 2. 先预放行 DeepSeek 固定命令（部署前必做）

1. 在有人在场的对话里手动跑一次：
   `/usr/bin/python3 -I -B /workspace/master/skill/scripts/deepseek_analyze.py --selftest`
2. 再手动跑一次真实 job（先用 Test job）；出现审批 → **Always allow**。
3. Settings → General → Auto-review → Custom Rules：添加 Allow 规则
   （模板在技能内 `references/runtime/approvals.md` §2.1）。
4. 连续跑 2–3 次确认不再弹卡；然后才启用 routine。
5. 注意：无人值守审批约 10 分钟过期且动作不执行；被拦 = 该 run 失败，下一轮补。

---

## 2.1 routine 里不要重定向 stdout

- 固定命令直接运行即可；**不要**在 routine 里写 `> /workspace/master/out/raw/...` 之类的
  重定向。raw 文件由 `deepseek_analyze.py` 自己原子写入（`.worker.stdout.json`）。
- `job_id` / `asof` 用 S0 的真实开始时间，不要用排期时刻。

## 3. 五个 routine 的 prompt（直接复制）

### 2.1 primary_babybus

- Schedule：`每天 07:30`（Asia/Shanghai）
- Prompt：

```text
使用 finance-master 技能，执行 references/runbooks/kol-primary.md。
参数：routine_id=primary_babybus, account=BabybusFL。
严格按技能内的数据包、置信度、建议卡契约执行：只读连接器；
不写 watchlist、不下单、不发邮件；结果按 runtime/delivery.md 的摘要格式输出。
```

### 2.2 primary_haochi

- Schedule：`每天 07:40`
- Prompt：同上，`routine_id=primary_haochi, account=haochihaochiaaa`。

### 2.3 primary_balder

- Schedule：`每天 07:50`
- Prompt：同上，`routine_id=primary_balder, account=Balder13946731`。
- 注意：**不打开 Balder 网站**，只读 X。

### 2.4 supplement

- Schedule：`每天 08:00`
- Prompt：

```text
使用 finance-master 技能，执行 references/runbooks/kol-supplement.md。
参数：routine_id=supplement, accounts=aleabitoreddit,jiaao_wu,KotlinerBTC。
严格按技能契约执行：只读 X 与 IBKR；不写 watchlist、不下单；按摘要格式输出。
```

### 2.5 holdings（持仓复核）

- Schedule：`每天 08:30`（美股收盘后；只跑一次）
- Prompt：

```text
使用 finance-master 技能，执行 references/runbooks/holdings-review.md。
参数：routine_id=holdings。
读取 IBKR + Schwab 全部持仓并逐仓判断（持有/加仓/减仓/卖出）；
不读 X；不写 watchlist、不下单；嘉信只读。按摘要格式输出。
```

---

## 4. 可选：一天两轮 / 三轮

- 推荐先跑 **2 轮/日**：把 2.1–2.4 各复制一份，时间改成 `20:30 / 20:40 / 20:50 / 21:00`；
  holdings 保持 1 次。
- 想 3 轮：再加 `12:30 / 12:40 / 12:50 / 13:00` 一份。先跑一周看用量再决定。
- 每次运行都会自动只读增量（时间窗 = 距上次成功，≤14 天），不会重复分析旧帖。
- X 读取预算：主账号 1–2 次/轮；补充 3–6 次/轮；每日合计约 10–20 次。

---

## 5. 手动触发与 webhook

- Bot 的 "Test" 会真实执行一次（会消耗 usage），首次可用它验证。
- 可用 webhook 触发（POST + `Authorization: Bearer <key>`）；没有结果回执，
  结果仍只在聊天里。不建议把 webhook 当主路径。

---

## 6. 出问题先看哪里

| 现象 | 先查 |
|------|------|
| routine 没输出 | Bot 聊天里的失败摘要；X / IBKR 连接 |
| 卡全是观望 | 数据包缺口（fundamentals/quote）；或 confidence 被压到 C |
| 没有 DeepSeek | 审批拦截/密钥缺失；看摘要里的 `analysis_source` |
| 重复分析旧帖 | 状态目录 `/workspace/master/state` 是否可写 |
| 技能未触发 | 手动发一次："按 finance-master 技能读我的持仓" |
