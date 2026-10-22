# Runbook · KOL 补充账号 routine

> 适用：`supplement`（@aleabitoreddit / @jiaao_wu / @KotlinerBTC，一次读完）。
> 定位：给三个主账号做补充/对照，也能带出主账号没写的票。
> 参数：`routine_id=supplement`。

---

## 1. 准备

1. S0 能力探测；读 `state/runs`、`state/advice`、`state/mentions.jsonl`。
2. `since` = 上次成功时间（上限 14 天）。
3. 读今日主账号已出卡/已提及的票（来自 `state/advice` + `mentions`）。

---

## 2. 读 X（3–6 次）

1. 三个账号各读 1 次时间线（`from:<handle>` + `since:`）。
2. 截断才补读主帖（每账号最多 +1，总数 ≤6）。
3. 抽字段规则同 `x-advanced-research` GUIDE；每账号只留 8 条原文，回复丢弃。
4. 写入 `state/mentions.jsonl`。

---

## 3. 选票规则（与主账号不同的地方）

1. **优先**：主账号今日已提到、补充账号也提到的票（交叉印证，但 X 相加仍只算 1 链）。
2. **其次**：补充账号单独提到、主账号近 14 天没写过的票（`source: supplement`）。
3. 取前 **≤3** 只分析、**≤2** 张卡；其余写"观察"。
4. 今日主账号已出过卡的票：不重复分析，摘要写"见今日该票卡"。

---

## 4. 组包与图

- 数据包按 `contracts/data-pack.md`；`source: supplement`。
- 持仓/行情/Web 采集同 `kol-primary.md` §3。
- 只用补充账号的帖子作为 KOL 证据；不把主账号旧帖搬进来。

---

## 5. 分析、决策、出卡

与 `kol-primary.md` §4–§5 相同：
worker（或 inline）→ 置信校验 → stance/target/sell → 建议卡。

注意：补充账号证据较弱时，`confidence` 可能只有 B/C；C 级不得买入。

---

## 6. 状态与交付

同 `kol-primary.md` §6；摘要标题写 `supplement`，并注明"补充 routine"。

---

## 7. 边界

- 不把补充账号当主账号：单独提到的票标 `source: supplement`。
- 不打开 Balder/Serenity/Koltracker 网站。
- 若三个账号都无新帖 → "无新增"，不重复分析。
- routine 内不写 watchlist、不下单。
