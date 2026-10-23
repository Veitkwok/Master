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

# Hindsight（2026-10-23 起 Cloudflare MCP；令牌不在本文件）
hindsight_connector: hindsight-sherlock-cf
hindsight_base_url: https://hindsight.veitkwok.us.kg/mcp/sherlock/
hindsight_tool_read: recall
hindsight_tool_write: sync_retain
hindsight_tool_bank: get_bank
hindsight_retry: 1
hindsight_failure_mode: non_blocking   # 失败继续跑，标 memory: missing

# 估值输入闸门（worker exit 8）
valuation_inputs_required: true
web_collect_attempts: 2          # exit 8 后补采并重跑的最多次数
allow_incomplete_after_attempts: true  # 仍缺 → allow_incomplete=true 让 worker 出 partial/null
peer_count_min: 3
valuation_routes: [dcf, comps]        # 至少一条完整
comps_lenses: ["eps_ttm+pe", "revenue_ttm+ev_sales", "ebitda_ttm+ev_ebitda"]
comps_min_peers_per_lens: 3
comps_wide_threshold: 3               # max/min > 3 -> wide_comps（降置信度，不 blocked）
comps_very_wide_width: 1.0            # (high-low)/base > 1.0 -> very_wide（C，不得买入/卖出）
target_quality_gate: B                # 触发 BUY/TRIM/SELL 的 target 最低质量

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
