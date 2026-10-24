# 目标价（target）

> 目标价只有一个来源：本轮估值输出（`company-valuation`：DCF / 可比 / SOTP）。
> 本文件规定如何把估值锚收成一个数字与一个区间，以及什么时候只能写 `null`。
> 卡字段见 `references/contracts/advice-card.md`；stance 消费 target 见 `decisions/stance.md`。

---

## 1. 输入

-worker 或 inline 引擎返回：

```text
dcf_fair: <number|null>          # DCF 每股公允价值
dcf_range: [lo, hi] | null       # DCF 敏感性区间（WACC × g）
comps_range: [lo, hi] | null     # ≥3 家可比公司给出的隐含区间
sotp_fair: <number|null>         # 仅多分部公司，可选
valuation_status: ok|partial|blocked
fields_gap: [...]                # 缺哪些输入（摊薄股数/FCF/peers...）
asof/source: 本轮数据包时点与来源
```

`valuation_status != ok` 或关键输入缺失 → 不得强行给数字（可给 `partial` 区间并降置信度）。

---

## 2. 收口规则（按顺序）

设 `comps_mid = (comps_low + comps_high) / 2`。

1. **DCF 与可比都有效**：
   - 若 `|dcf_fair − comps_mid| / max(dcf_fair, comps_mid) ≤ 25%`：
     `target.base = 0.5 × dcf_fair + 0.5 × comps_mid`，`basis = dcf_blend`；
     `target.low = min(dcf_range.lo, comps_low)`，`target.high = max(dcf_range.hi, comps_high)`。
   - 若分歧 > 25%：取**保守值** `target.base = min(dcf_fair, comps_mid)`，
     `basis = dcf_blend`，置信度上限 **B**，`limiting` 加"估值分歧 >25%"。
2. **只有 DCF**：`target.base = dcf_fair`，`basis = dcf`；
   `low/high = dcf_range`；无敏感性区间则 `base × [0.85, 1.15]` 并标"区间为假设"。
3. **只有可比**：`target.base = comps_mid`，`basis = comps`；`low/high = comps_range`。
4. **只有 SOTP**（多分部且数据完整）：`target.base = sotp_fair`，`basis = sotp`；
   区间用分部敏感性 `±10%`，标 `basis_note`。
5. **都不成立**：`target.base = null` → 不允许 BUY；卡上写"目标价缺失：<fields_gap>"。

数值规则：保留 2 位小数；不写超出区间来源的精确度（禁止"目标价 223.87 元"式的假精度，
若输入只有区间则取区间中值并注明）。

### 2.1 可比法的分散处理

- ≥3 家 peers + 匹配倍数即可算；**分散不构成 blocked**。
- `target.base = 同业隐含价的中位数`；`low/high = 25/75 分位`（或 min/max，注明）。
- `max(peers)/min(peers) > 3` → 标 `wide_comps`，置信度上限 **B**，`limiting` 加"同业分散"。
- 隐含价区间宽度 > 中位数的 100% → 标 `very_wide`，置信度 **C**，卡上可显示 target 但
  不得据此买入（stance 只能 WATCH/HOLD）。
- 负 FCF / 无 DCF 时**必须尝试可比法**；只有"匹配倍数不够 3 家"才允许 target=null。

### 2.2 脚本确定性可比回退（`computed_comps`）

worker 仍不给 `comps_range` 时，worker 脚本会**自己**按本文件规则、用数据包里的 peers
算一份确定性的 `computed_comps`（写在 stdout/result 每票下）：

```text
computed_comps: {lens, base, low, high, peers_used, peers_count,
                 median_multiple, dispersion_ratio, width_ratio,
                 quality: ok|wide|very_wide|insufficient,
                 confidence_cap: B|C, upside_pct}
```

Bot 收口顺序（v1.0.13 起）：
1. worker 的 `valuation.dcf_fair` 有效 → 用它（DCF）；
2. 否则用脚本 `computed_comps`（basis 写 `comps(script)`，卡上注明脚本计算）——
   **优先于 worker 的 comps_range**；
3. 只有在脚本没有可用 computed_comps 时，才接受 worker 的 `comps_range`，
   且必须能列出 peer 倍数与计算式（不可溯源 → 作废）；
4. 都没有 → target null。

卡字段：`target_source: worker_dcf | script_comps | worker_comps | null`。

`computed_comps.quality` 判定（脚本执行，写进 stdout）：

| 条件 | quality | cap |
|------|---------|-----|
| 同业 max/min ≤3，且区间宽度 ≤100%，且 \|upside\| ≤200% | `ok` | B |
| 同业 max/min >3，或宽度 >100%，或 \|upside\| >50% | `very_wide` | C |
| 同业 max/min >**10** | `very_wide` | C |
| base > 5×现价 或 base < 0.2×现价 | `insufficient` | C（不可用） |

- 多 lens 时：先按 quality（ok→wide→very_wide→insufficient）、再按 |upside| 最小、
  再按区间宽度选一个 lens（避免挑中"看起来精确但荒谬"的倍数）。
- `very_wide` 可以把 target 显示在卡上（供参考），但**不得据此买入**；
  `insufficient` 不显示为 target，只写"估值输入不可用"。
- `very_wide`/`insufficient` **不得仅因 target 触发减仓/卖出**（见 stance.md）。

---

## 3. 时间尺度与复核

- `horizon` 固定 `6-12m`（估值锚，不是时点承诺）。
- `review_by` = 下一次财报日 或 `asof + 90 天`，取更早者。
- 财报/重大事件后目标价必须重算，不得沿用旧值。
- 到达目标价即按 `decisions/sell.md` 分批止盈，不必等 12 个月。

---

## 4. entry_limit（不追高线）

```text
min_upside = 20%（新买）/ 15%（加仓），写在 config
entry_limit = min(last × 1.02, target.base × (1 − min_upside))
若 last > entry_limit → stance 只能 WATCH（不追）
```

- `entry_limit` 不得高于 `target.base × 0.85`（保证至少 15% 赔率），也不得高于
  现价 +2%（避免"追高"）。
- 用户明确要求"市价买"时仍先展示 entry_limit 与赔率，再给出选择。

---

## 5. ETF 的目标价

- ETF 无 FCF，**不用 DCF**。
- 有 NAV / 发行商数据 / 估值带（`etf` 模块 M1–M7）时：
  `target.base = band_mid`（或 NAV 溢价修复目标），`basis = etf_band`，注明方法。
- 无可靠 NAV/band → `target.base = null`，ETF 只能 `HOLD/WATCH`，不给买入。
- 分红率/分配率不是目标价依据；总回报口径见 ETF 模块。

---

## 6. 禁止

- 不采用 KOL 口播目标价、卖方目标价、记忆里的旧目标价、技术位/画线位作为 target。
- 不在缺输入时用"行业平均倍数"硬凑一个数字。
- 不把 `priced_in`/`trap` 的结果拼进 target（它们是门槛，不改估值）。
- 不写"目标价 = 现价 × 1.3"这类无估值依据的数。

---

*target v1 · DCF / 可比收口 · 缺输入则 null*
