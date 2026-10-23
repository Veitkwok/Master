# 运行时 · 连接器能力与工具发现（capabilities）

> Grok Bot 的连接器工具名不公开、可能变化。**按能力找工具，不硬编码工具名。**
> 本文件列出每类能力、探测方法、只读/可写边界、失败表现。

---

## 1. 能力清单

| 能力 | 用途 | 读/写 | 探测 |
|------|------|-------|------|
| IBKR 行情 | 现价/快照/历史K线/期权链/主题 | 只读 | 调用一次 quote（如快照/最新价） |
| IBKR 账户 | 持仓、余额、成交 | 只读 | 读一次 positions |
| IBKR watchlist | Favorites / ETFs / Assets / Nasdaq-QQQ + Candidate | 读；Candidate 可追加 | 列出 watchlists |
| IBKR 草稿/订单 | AI Instructions / 草稿 | 写（仅人工确认） | **不探测、不调用** |
| X 读取 | 时间线/关键词/帖子/线程 | 只读 | 读目标账号最新 1 条 |
| Hindsight | `get_bank` / `recall` / `sync_retain`（连接器 `hindsight-sherlock-cf`） | 读写（仅 sherlock） | `get_bank` 一次 |
| Schwab（Plaid/Finance） | 持仓、交易记录 | 只读 | 读一次 positions |
| Web 浏览/搜索 | 财报、发行商页、新闻 | 只读 | 打开一个页面 |
| 文件/状态 | /workspace 读写 | 读写 | 写一个临时文件 |
| Python/终端 | DeepSeek worker、校验脚本 | 执行 | `python3 --version` |
| Secret | DEEPSEEK_API_KEY | 只读（环境变量） | 检查是否存在（不打印值） |
| 交付 | 聊天、文件、Page | 写 | 直接使用 |

---

## 2. 探测流程（S0）

```text
1. ibkr = try(read positions) -> live / down
   if live: watchlists = try(list watchlists) -> [Favorites, ETFs, Assets, Nasdaq-QQQ, Candidate?]
2. x = try(read one target account timeline, limit=1) -> live / down
3. hindsight = try(recall ticker or generic) -> live / down
4. schwab = connector present ? try(read positions) : skip
5. state = try(write /workspace/master/state/.probe) -> ok / readonly
6. deepseek = only when analysis needed -> scripts/deepseek_analyze.py --selftest
```

每项超时短（≤15s），失败写 `source_error` 并继续；**不要因为一个连接器失败中止整轮**。

---

## 3. 工具发现规则

- 先列当前 Bot 可用的工具/连接器（如有 list tools 能力），再按**语义**匹配：
  - 持仓 → "positions / portfolio / holdings"
  - 现价 → "quote / price / snapshot"
  - 历史 → "history / bars / candles"
  - 观察列表 → "watchlist"
  - 下单/草稿 → "order / instruction" → **默认禁用**
- 匹配不到 → 记为 `connector: unsupported`，按降级矩阵处理；**不要自己拼 API**。
- 工具名/参数写进 run 状态（`connector_map`），方便下次复用与排错。

---

## 4. 权限边界（硬）

| 连接器 | 允许 | 禁止 |
|--------|------|------|
| IBKR | 行情、持仓、余额、成交、watchlist 读、Candidate 追加（用户确认） | 下单、改其他四张表、删表、重排 |
| X | 公开推文只读 | 发帖、私信、改账号 |
| Hindsight | `sherlock` 读/写（recall / sync_retain） | `hermes` / `sissyfication` 写入、delete、改 bank 配置 |
| Schwab | 持仓、交易记录只读 | 任何写操作、下单、watchlist |
| Web | 公开页面读取 | 登录付费墙、绕过限制 |
| Secret | 读取环境变量使用 | 打印/写文件/进聊天 |

---

## 5. 已观测连接器（2026-10-23）

| 连接器 | 实际名称 | 状态 |
|--------|----------|------|
| IBKR | `Interactive Brokers (IBKR)-xai` | 正常：行情/持仓/watchlist 可读 |
| X | 内置 `x` | 正常 |
| Schwab | `Finance-xai`（Plaid，只读） | 正常：读到持仓与现金；无 watchlist |
| Hindsight | `hindsight-sherlock-cf`（Cloudflare MCP · Streamable HTTP） | 正常（三个 bank 实测）；依赖 Mac Mini + cloudflared + Caddy 网关 |

watchlist 实测名：`Favorites`、`ETFs`、`Assets`、`Nasdaq-QQQ`、`Candidate`
（匹配时大小写不敏感、单复数兼容）。

### 5.1 实测工具名（2026-10-23，Bot 运行记录）

| 能力 | 实际工具 |
|------|----------|
| IBKR 行情 | `get_price_snapshot`、`get_price_history` |
| IBKR 账户 | `get_account_positions` |
| IBKR watchlist | `get_watchlists`（列表）、`get_watchlist`（单表） |
| X 读取 | `search_posts_all`（支持 `from:`）、`get_users_posts` |
| Schwab | `finance_list_portfolio_holdings`（Plaid 只读） |
| Web | `tavily_search`、`WebFetch`（WebFetch 优先用于 stockanalysis/发行商页；curl 可能被站点拦截） |
| Hindsight | `get_bank`、`recall`、`sync_retain` |

这些只是当前 Bot 的映射示例；代码/契约仍按能力调用，工具名变化时以探测为准。
Hindsight 探测：最多重试 2 次（间隔 ~2s）；仍失败就记 `hindsight: down`，
继续本轮并在摘要标注——**不阻断**。

### 5.2 Hindsight（2026-10-23 迁移后 · Cloudflare）

```text
Bot 连接器（hindsight-sherlock-cf / hindsight-cf / hindsight-sissyfication-cf）
  → https://hindsight.veitkwok.us.kg/mcp/<bank>/   (X-Hindsight-Token)
  → Cloudflare 边缘 → Tunnel（Mac Mini 上 cloudflared 主动外连）
  → Caddy 令牌网关 127.0.0.1:8889 → Hindsight 127.0.0.1:8888（OrbStack）
```

- 三个连接器分别接 `hermes` / `sherlock` / `sissyfication`；Master 只用
  **`hindsight-sherlock-cf`**，工具 `get_bank`、`recall`、`sync_retain`。
- 令牌存在 Bot 连接器请求头 + Mac Mini `~/.hindsight-gate/token`（600）+
  维护者电脑副件；**不写进技能/仓库/聊天**。
- 验证（任何人都可在有令牌的机器上跑）：

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://hindsight.veitkwok.us.kg/health   # 401
curl -s -H "X-Hindsight-Token: $HINDSIGHT_TOKEN" https://hindsight.veitkwok.us.kg/health
```

- 失败判断：401 = 令牌/请求头；502/521 = cloudflared 或 Caddy 没跑；超时 = Mac Mini
  离线/断网。Bot 侧重试 1 次后按 `hindsight: down` 处理，不阻断本轮。

## 6. 已知不稳定项

- **IBKR**：用户已确认当前正常；若 OAuth 失效 → `ibkr: down`，不出买卖卡。
- **Hindsight**：走 Cloudflare Tunnel + Caddy；依赖 Mac Mini 常开与 cloudflared 进程。
  失败按 `hindsight: down` 处理，不阻断（2026-10-23 起 Tailscale 方式已弃用）。
- **Schwab**：第三方连接器；工具/字段可能变化 → 按能力发现，缺就 skip。
- **X**：内置只读，通常稳定；失败不要用网页镜像替代原帖。

---

## 7. 降级输出

```yaml
connectors:
  ibkr: live|down
  x: live|down
  schwab: live|down|skip
  hindsight: live|down
  state: ok|readonly
  deepseek: ok|unavailable|blocked
connector_map:
  quote: "<实际工具名>"
  positions: "..."
  watchlists: "..."
  x_timeline: "..."
  hindsight_recall: "..."
  schwab_positions: "..."
```

把这张表放进 run 状态与摘要（摘要只显示一行状态）。
