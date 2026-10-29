# 运行时 · 状态与幂等（state）

> 状态放在技能包外：**`/workspace/master/state/`**（Bot 电脑持久盘）。
> 技能更新/重装不丢；`routine` 历史只有 20 条，不能当状态用。
> 所有写入用"追加 + 原子替换"；同一天重复运行不得重复出卡。

---

## 1. 目录

```text
/workspace/master/
├── state/
│   ├── runs/YYYY-MM-DD.json          # 当天各 routine 的运行记录
│   ├── mentions.jsonl                # 14 日提及（KOL 频率用）
│   ├── advice/YYYY-MM.jsonl          # 建议卡归档（逐行 JSON）
│   ├── pending_candidates.json       # 待用户确认的 Candidate
│   ├── watchlists/YYYY-MM-DD.json    # 四张表快照（只读采集）
│   ├── peers/YYYY-MM-DD.json         # 当轮采到的同业倍数（同日复用）
│   ├── fundamentals/YYYY-MM-DD.json  # 当轮采到的财务/股数/净债（同日复用）
│   └── .probe                        # 可写探测
├── out/                              # 每日摘要与卡的文件版
│   ├── YYYY-MM-DD-<routine>.md
│   ├── cards/YYYY-MM-DD/<SYM>.md
│   └── raw/<YYYYMMDD-HHMMSS-mmm-nonce>-<routine>-<job_id>.worker.stdout.json|.worker.exit
│                                    # 脚本自己写（v1.0.18 起；原子写、合法 JSON；带 .worker 防撞名）
└── packs/                            # 本轮数据包（调试/复现；可清理）
```

---

## 2. 文件 schema

### 时间戳语义（v1.0.15 起 · 修正）

- **run 记录**：`started`（S0 开始）/ `finished`（S8 结束），真实时钟、ISO+08；
- **`job_id` / `asof` 必须用真实开始时间**：S0 开始时取本机时钟，**不得使用排期时间**
  （例：排期 08:02 但实际 07:56 开始 → job_id/asof 都用 07:56）；
- **卡片 `asof` = 卡片生成/写盘时刻**：写卡前一刻取时间，立刻写文件；
  `asof` 与文件 mtime 差必须 **≤2 分钟**；**禁止**用 run `started`/`finished` 当卡 asof，
  也禁止收尾后补写"now"；
- `price_asof` = 行情时点（IBKR 报价/收盘/盘后）；
- 卡面第一行固定 `运行: <status> · <reason>`；持仓卡另带 `集中度:` / `接近失效:` 行。

### run 生命周期与失败记录（v1.0.19 起）

1. **S0 第一件事**：往 `runs/YYYY-MM-DD.json` 追加一条
   `{routine, account, job_id, started, status:"running"}` —— 在 X/IBKR/Web 采集之前写；
2. **S8**：更新 `finished` / `status`（succeeded|partial|failed）/ `result` / `cards` / `errors`；
3. **任何异常**：写 `status:"failed"` + `error_class` + `finished`；
4. **中断恢复**：下一轮开始先扫当日 `runs`，若某条 `running` 且 `started` 超过 2 小时
   → 改成 `status:"failed"`, `error_class:"interrupted"`，并在摘要里报"某 routine 被中断"；
5. **日检/报告 routine**：检查 5 条 routine 是否都有终态记录；缺记录 → 报
   `failed(no_record)`，不算成功；
6. 任何一次运行（含失败/中断）都必须在 `state/runs` 留痕；**不允许"什么都没留下"**。

### 状态语义（runs / 摘要共用）

- `succeeded`：本轮输出完整，无 target null 因缺数据、无关键 connector down；
- `partial`：跑完但有卡缺 target/字段，或 connector down（Hindsight/Web/估值）；
- `failed`：run 中止（审批卡住/脚本异常/关键依赖不可用）。

### `runs/YYYY-MM-DD.json`

```json
{
  "date": "2026-10-23",
  "runs": [
    {
      "routine": "primary_babybus",
      "started": "2026-10-23T07:30:00+08:00",
      "finished": "2026-10-23T07:36:00+08:00",
      "status": "ok|partial|failed",
      "connectors": {"ibkr": "live", "x": "live", "hindsight": "live",
                      "schwab": "skip", "state": "ok", "deepseek": "ok"},
      "analysis_source": "deepseek|bot-inline|mixed",
      "deepseek_status": "ok|failed|blocked|skipped",
      "deepseek_error_class": "config|network|json|truncated|rate_limit|timeout|approval|null",
      "deepseek_thinking": "on|off",
      "deepseek_usage": {"prompt_tokens": 0, "completion_tokens": 0},
      "deepseek_cache_hit": 0,
      "tickers_seen": ["NVDA", "MRVL"],
      "cards": ["NVDA"],
      "skipped": [{"symbol": "MRVL", "reason": "target_missing"}],
      "candidates_proposed": ["NVDA"],
      "errors": [],
      "next_catchup_from": "2026-10-22T20:40:00+08:00"
    }
  ]
}
```

### `mentions.jsonl`（一行一条）

```json
{"date":"2026-10-23","handle":"BabybusFL","symbol":"NVDA","url":"https://x.com/...","routine":"primary_babybus","line":"原句摘要≤120字"}
```

- 同一 `url + symbol` 只留一行；保留 14 天（运行开始时清理更早的）。
- `handle` 不带 `@`。

### `advice/YYYY-MM.jsonl`

```json
{"date":"2026-10-23","routine":"primary_babybus","symbol":"NVDA","stance":"BUY","target":224.0,"invalidation":158.0,"trap_level":"green","confidence":"B","analysis_source":"deepseek","card_ref":"out/cards/2026-10-23/NVDA.md"}
```

- 用于"同票同日只出一次"和跨日对照。
- 每行只记卡的关键字段，不记完整卡（完整卡在 `out/cards/`）。

### `pending_candidates.json`

```json
{"NVDA": {"first_seen": "2026-10-20", "mentions_14d": 3, "accounts_14d": 2,
           "conviction": "high", "proposed_on": ["2026-10-23"], "confirmed": false}}
```

### `watchlists/YYYY-MM-DD.json`

```json
{"asof":"2026-10-23T07:31:00+08:00",
 "Favorites":["NVDA"],"ETFs":["SMH"],"Assets":["SGOV"],"Nasdaq-QQQ":["QQQ"],
 "Candidate": []}
```

- 只读快照；Candidate 不存在时写 `[]` 并在摘要提示"未建立"。表名大小写/单复数不敏感。

---

## 3. 幂等规则

1. **run 开始**：读 `runs/YYYY-MM-DD.json` 与 `advice/`。
2. **时间窗**：`since = last_success(routine) `，上限 14 天；帖子/代码去重。
3. **同票同日**：`advice/` 已有该票今日卡且无新证据 → 摘要"见今日该票卡"，不再出卡。
4. **holdings**：每天只跑一次；若已有今日记录 → 跳过（除非用户手动要求重跑）。
5. **失败**：写 `status: failed` + `errors`；不自动重试；下一轮按 `next_catchup_from` 补。
6. **写文件**：先写 `.tmp` 再 `mv` 覆盖；读-改-写同一文件时避免并发（单 Bot 顺序）。

---

## 4. 恢复

- 状态目录丢失/不可写：
  - 本 run 用内存去重；
  - 从 `out/`、Hindsight case、`pending_candidates` 尽力重建；
  - 摘要标注 `state: readonly/lost`，并提示用户检查 `/workspace/master`。
- 重装技能不影响状态（技能在 `~/agent-data/workflows/`，状态在 `/workspace`）。

---

## 5. 维护

- 每周清理：`packs/` 保留 7 天；`out/` 保留 90 天；`runs/` 保留 90 天。
- 不把状态写进技能目录（防止重装丢失/污染 skill 加载）。
- 状态文件不包含密钥、完整账户号；持仓只保留卡需要的字段。
- `out/`、`out/raw/`、`runs/` 保留 90 天（不要每天清空；Day 0 报告丢失就是反例）。

---

*state v1 · 四本账 · 同票同日一张卡 · 失败不重试*
