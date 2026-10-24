# 建议卡契约（唯一输出）

> 用户看到的**唯一一张**买入 / 目标价 / 卖出卡。任何引擎模块的结论都收口到这里。
> 判断规则在 `references/decisions/`；本文件只定义字段、格式、校验与摘要格式。

---

## 1. 卡片字段（机器可读，逐票）

```yaml
card_version: 1
asof: 2026-10-23T07:34:00+08:00
price_asof: "2026-10-22 close ET / IBKR"
routine: primary_babybus | primary_haochi | primary_balder | supplement | holdings | adhoc
symbol: NVDA
name: NVIDIA Corp
asset: stock | etf
source: primary | supplement | holding | user
thesis: "一句可证伪的论点"
kol_evidence:
  - handle: BabybusFL
    url: https://x.com/...
    posted_at: 2026-10-21T13:05:00Z
    line: "作者原句（可截断，不改写）"
stance: BUY | ADD | HOLD | TRIM | SELL | AVOID | WATCH
action_cn: 买入 | 加仓 | 持有 | 减仓 | 卖出 | 回避 | 观望
last: 182.40
entry_limit: 186.00          # 买入/加仓上限；不追高
target:
  base: 224.00               # 目标价（唯一数字）
  low: 205.00
  high: 243.00
  basis: dcf_blend | dcf | comps | etf_band | null
  source: worker_dcf | script_comps | worker_comps | null
  horizon: 6-12m
upside_pct: 22.8
sell_plan:
  ladder:                    # 分批止盈
    - at: 224.00
      fraction: "1/3"
    - at: 243.00
      fraction: "1/3"
  remainder_rule: "剩余 1/3 用失效条件 + 下次复核守护"
  invalidation_price: 158.00
  invalidation_thesis: "下季指引下调 / 连续 3 日收盘 < 50 日线"
  review_by: 2027-02-20      # 下次财报或 90 天
position:
  context: neither | ibkr | schwab | both
  qty: null
  avg_cost: null
  market_value: null
  unrealized_pct: null
  cash_note: "用户未说现金 → 不写金额"
risk:
  trap_level: green | yellow | orange | red | null
  priced_in: not_priced | partial | priced | gap | null
  confidence: A | B | C
  limiting: [无一手文件]
  chains: "IBKR+WEB"
  key_risks: ["客户集中度"]
  overlap: ["已持 QQQ，科技暴露叠加"]
  concentration: "top2 AI capex 93% | null"   # 持仓复核用；≥80% 必须标注
data_gaps: []
analysis_source: deepseek | bot-inline | mixed
order_sent: false
schwab_trade: forbidden
draft_created: false
```

## 2. 卡片展示格式（聊天里）

```text
## NVDA · 买入候选 · primary_babybus
asof 2026-10-23 07:34 +08 | 价格时点 2026-10-22 收盘（IBKR）
现价 $182.40 | 持仓：IBKR 12 股 @ $171.20（+6.5%）| Schwab 无
stance: 买入（新买）| 证据 B | trap green | priced_in partial
买入上限: $186.00（现价不高于上限才买，不追高）
目标价: $224.00（区间 $205–$243，6–12 月，DCF+可比）| 上行 +22.8%
卖出计划: $224 减 1/3 → $243 再减 1/3 → 余仓跌破 $158 或论据失效全出
失效条件: 下季指引下调 / 连续 3 日收盘 < 50 日线 / 跌破 $158
复核: 下次财报（2027-02 前后）或 90 天
风险: 客户集中度；10Y +50bp → DCF −8% | 重叠: 已持 QQQ
缺口: 无 | 分析: deepseek
未下单 · 未写嘉信 · 本卡不构成委托
```

## 3. 必填与允许缺失

- 必填：`asof`、`symbol`、`stance`、`last`、`position.context`、`confidence`、
  `order_sent:false`、`schwab_trade:forbidden`。
- 条件必填：
  - `BUY / ADD`：`entry_limit`、`target.base`、`sell_plan.invalidation_price`、
    `sell_plan.invalidation_thesis`、`confidence ≥ B`；
  - `TRIM / SELL`：`target` 或 `invalidation` 至少一个触发原因；
  - `AVOID`：`trap_level` 为橙/红，或明确写出回避原因。
- 允许 `null`：目标价（→ 不得 BUY）、失效价（→ 不得 BUY）、持仓（→ 新买或未知）、
  现金金额（用户没给就不写）。

## 4. 校验清单（Bot 出卡前逐条过）

- [ ] stance 与 `decisions/stance.md` 的优先级表一致；
- [ ] `target.base` 能指回本轮估值输出（`company-valuation` 或 worker 的
      `dcf_fair`/`comps_range`）——指不回就作废；
- [ ] 买入上限合理：`last ≤ entry_limit` 且 `entry_limit ≤ target.base × 0.85`
      （最低 15% 赔率；默认 20% 见 stance）；
- [ ] 无失效条件 → 不得 BUY/ADD；
- [ ] trap 橙/红 → 不得 BUY/ADD；
- [ ] X 纯社交证据 → grade 不得 ≥ B；
- [ ] `order_sent`/`draft_created` 恒为 false；`schwab_trade` 恒为 forbidden；
- [ ] 每个数字有时间点与来源；
- [ ] 同票同日只有一张卡（查 `advice/` 状态）。

## 5. 每日摘要格式

```text
📅 2026-10-23 · primary_babybus · 07:32 +08
数据: IBKR✅ X✅(1 read) Hindsight✅ Schwab→skip DeepSeek✅
扫描: 2 账号帖 → 3 只候选 → 2 张卡 + 1 只观察

【卖出/减仓】XYZ · 卖出（Schwab 仓，成本 $120.00，现价 $25.00，-79.2%）
  失效已触发（论点破裂 + 跌破 $60）；建议手动清仓；本卡不代下单。

【买入】NVDA · 买入（新买）$182.40 → 目标 $224，上限 $186
【观察】MRVL · 观望：目标价缺失（估值输入不足）
【Candidate 提议】NVDA 14 日 3 次 / 2 个账号 / 确定性 high → 回复确认后写入

缺口: 无 | 未下单 · 未写观察列表（Candidate 待确认）
```

## 6. Candidate 提议格式（只提议，不自动写）

```text
建议加入 Candidate：NVDA（14 日 3 次 / 2 个账号 / 确定性 high）。
回复"确认写入 NVDA"后，我只追加到 Candidate；不删、不重排其他四张表。
Candidate 尚未建立时：只提示，不创建。
```

## 7. 禁止

- 不写第二张卡、不写"评级上调/下调"式卖方话术、不写"保证/稳赚"。
- 不把 KOL 目标价、记忆价格、技术位当 `target`。
- 不声称已成交/已下单；不生成嘉信订单；不把嘉信仓写成 IBKR 草稿。
- 不省略"未下单"页脚。
