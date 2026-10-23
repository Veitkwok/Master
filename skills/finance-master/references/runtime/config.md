# 运行配置（owner 阈值 · 2026-10-23）

> 一张表集中放可调参数，避免阈值散落在契约里。改这里 = 改行为；
> 改完在 CHANGELOG 记一行，并跑 `dev/check_pack.py`。

```yaml
# 买入 / 加仓
min_upside_new_buy: 0.20        # 新买最低上行（target.base / last - 1）
min_upside_add: 0.15            # 已持有加仓最低上行
entry_max_premium_vs_last: 0.02 # entry_limit 不得高于现价 2%（不追高）
entry_limit_cap_vs_target: 0.85 # entry_limit ≤ target.base × 0.85（至少 15% 赔率）
min_confidence_buy: B           # 买入/加仓最低证据等级（A|B|C）

# 失效 / 卖出
max_loss_pct_new_position: 0.15 # 仅新买入：entry_limit × (1-15%) 入场止损
max_drawdown_stop_existing: off # 已持有：不设成本止损（owner 2026-10-23：继续持有）
held_invalidation: structure+thesis  # MA50/MA200/前低 + 论据，必须带确认窗口
sell_ladder: "1/3 at target.base; 1/3 at target.high; remainder invalidation/review"
review_by: "min(next earnings, asof + 90d)"

# 闸门
trap_buy_gate: [green, yellow]  # orange/red 不给买点
priced_in_buy_gate: [not_priced, partial]

# 每轮预算
max_analyzed_per_routine: 3
max_cards_per_routine: 2
web_queries_per_ticker: "2-3 (financials + peers; ETF issuer page)"
x_reads_primary: "1-2 per run"
x_reads_supplement: "3-6 per run"

# 估值输入闸门（worker exit 8）
valuation_inputs_required: true
web_collect_attempts: 2          # exit 8 后补采并重跑的最多次数
allow_incomplete_after_attempts: true  # 仍缺 → allow_incomplete=true 让 worker 出 partial/null
peer_count_min: 3
peer_multiples_any: [pe, fwd_pe, ev_sales, ev_ebitda]

# Candidate
candidate_min_mentions: 2
candidate_min_accounts: 2
candidate_single_account_mentions: 3
candidate_exclude_held: true     # 已持仓不提议（owner 2026-10-23）
candidate_write: "only after user confirmation, append only"

# DeepSeek
deepseek_model: deepseek-flash    # pro only via DEEPSEEK_MODEL=deepseek-v4-pro
deepseek_thinking_routine: disabled
deepseek_thinking_deep: enabled
```
