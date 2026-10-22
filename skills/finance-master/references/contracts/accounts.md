# 账号与 routine 契约

> 六个账号、四条 routine 的映射、X 读取预算、候选阈值。**这是名单的唯一来源**，
> 引擎或其他文件不得保留第二份账号表（旧的 85 号表已作废，不迁移）。

---

## 1. 账号

| routine | 账号 | 说明 |
|---------|------|------|
| `primary_babybus` | @BabybusFL | 主账号，低频率，单独 routine |
| `primary_haochi` | @haochihaochiaaa | 主账号，低频率 |
| `primary_balder` | @Balder13946731 | 主账号；**不打开 Balder 网站** |
| `supplement` | @aleabitoreddit | 补充账号（三个共用一个 routine） |
| `supplement` | @jiaao_wu | 补充 |
| `supplement` | @KotlinerBTC | 补充 |

- 用户新增/更换账号：只改本文件一行；routine 参数使用 handle。
- 主账号帖子被截断才补读主帖；补充账号同理。
- 不扫这六个账号以外的时间线（用户点名 ad-hoc 除外）。

---

## 2. 排期（Asia/Shanghai，建议）

| routine | 频率 | 建议时刻 | 说明 |
|---------|------|----------|------|
| primary_babybus | 2 次/日（可 3 次） | 07:30 / 20:30 | 增量窗口，去重 |
| primary_haochi | 2 次/日（可 3 次） | 07:40 / 20:40 | 同上 |
| primary_balder | 2 次/日（可 3 次） | 07:50 / 20:50 | 同上 |
| supplement | 2 次/日 | 08:00 / 21:00 | 三个账号一次读完 |
| holdings | 1 次/日 | 08:30 | 美股收盘后；不读 X |

- 若要 3 次/日：加一轮 12:30 附近，复制对应 routine 即可（Bot routines ≤50）。
- 相邻 routine 间隔 ≥5 分钟（平台限制）。
- 平衡 usage：默认 2 次/日；3 次/日是可选档，先跑一周看用量再决定。
- 每次运行的时间窗 = min(距上次成功, 14 天)；按帖子/代码去重，不重复分析。

---

## 3. X 读取预算

| 场景 | 每轮读取上限 |
|------|--------------|
| 主账号 routine | 1 次时间线；截断才 +1（最多 2） |
| supplement routine | 3 次（每账号 1 次）；截断最多 +3（最多 6） |
| ad-hoc 点名 X 研究 | 8–15 次 |
| 每日合计（2 次/日档） | 约 10–16 次，远低于平台限额 |

- 只保留最新 8 条原始推文/账号，回复丢弃。
- 不为了凑频率重复扫同一时间线；没有新帖就报"无新增"。

---

## 4. 候选（Candidate）阈值

提议加入 Candidate 的条件（满足任一）：

- 14 日内 **≥2 次提及 且 ≥2 个账号**；
- 或 14 日内**单账号 ≥3 次**；
- 且 `conviction_hint != none`（原句至少有一个方向）。

输出格式与"只提议、确认后写"的流程见 `contracts/advice-card.md` §6。
写入动作只在用户在场的对话里执行；routine 只提议。

---

## 5. 提及日志（供频率统计）

- 路径与 schema 见 `runtime/state.md`（`state/mentions.jsonl`）。
- 每条：`date, handle, symbol, url, routine, line(原句摘要)`。
- 同一链接同一代码只留一行；保留最近 14 天。
- 频率只用于候选提议，不构成买入理由；热度不是证据链。

---

## 6. 边界

- 主账号与补充账号的关系：补充账号用于对照/补漏；其单独提到的票
  `source: supplement`，不因"非主账号"而不出卡。
- KOL 帖子只是发现（discovery），不是置信链；目标价永远来自估值。
- 不访问 Balder / Serenity / Koltracker 等第三方网站。
