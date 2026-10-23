# Hindsight 连接诊断（2026-10-23 14:32，Mac Mini 本机）

Bot 报告：`get_bank` 连 `100.114.80.63:8888` 超时；没有 `list_banks` 工具。
本机诊断结论：**Hindsight 服务本身是健康的**，问题在 Bot ↔ Mac Mini 的链路或
Bot 侧连接器状态，不是数据/服务故障。

## 1. 本机事实（Mac Mini，hostname `Veits-Mac-mini.local`，Tailscale `100.114.80.63`）

| 检查 | 结果 |
|------|------|
| 8888 监听 | OrbStack 转发；Docker 容器 `hindsight-agent-memory`（`ghcr.io/vectorize-io/hindsight`）映射 `0.0.0.0:8888->8888` |
| `GET http://127.0.0.1:8888/health` | `200 {"status":"healthy","database":"connected","db_pool_idle":3}` |
| `GET http://100.114.80.63:8888/health` | 同上（本机经 tailnet IP 访问正常） |
| `GET /v1/default/banks` | 正常返回 `sissyfication`、`hermes`、`sherlock` 三个 bank |
| `/mcp` | `200`（MCP 端点存在） |
| `/docs`、`/openapi.json` | 正常 |

Banks（截至诊断时）：

- `sherlock`：fact_count ~28，mission = US-equity research journal（写 case/复盘用）
- `hermes`：fact_count ~3834，共享长期记忆（**不写**）
- `sissyfication`：项目 bank（不碰）

## 2. Tailscale 事实

`tailscale status`（Mac Mini）：

```text
100.114.80.63    veits-mac-mini     macOS    -
100.82.228.101   grok-bot-vm-2      linux    active; relay "cn"; offline, last seen 1h ago
100.120.164.126  grok-bot-vm-1      linux    offline, last seen 4d ago
100.83.137.32    grok-bot-vm         linux    offline, last seen 11h ago
```

- 从 Mac Mini `tailscale ping 100.82.228.101` → `pong via DERP(cn) ~230ms`（链路可达）。
- Bot 节点是 **grok-bot-vm-2（100.82.228.101）**；`grok-bot-vm-1`、`grok-bot-vm` 已过期，
  需要在 Tailscale 管理后台删除（CLI 无法删其他节点）。

## 3. 判断

1. 服务健康、bank 都在、端口通 → **不是 Hindsight 数据问题**。
2. Bot 报 timeout：优先怀疑 **Tailscale 中继（DERP cn）偶发不稳 / Bot 侧 connector 卡住**，
   与之前"Hindsight 偶发掉线"一致。
3. `list_banks` 工具不存在是正常的：Bot 连接器暴露的是 `get_bank`；列 bank 用 HTTP API
   `GET /v1/default/banks`，不是 MCP 工具。

## 4. Bot 侧排查命令（下次 Bot 在线时跑）

```bash
# 1) 网络
curl -m 5 -s -o /dev/null -w "%{http_code}\n" http://100.114.80.63:8888/health
curl -m 5 -s http://100.114.80.63:8888/v1/default/banks | head -c 300
# 2) tailscale
tailscale status | grep -E "grok-bot|mac-mini"
tailscale ping 100.114.80.63
# 3) 若 curl 超时但 ping 通：检查 Bot 的 Tailscale ACL / 防火墙 / connector 重启
```

## 5. 处理建议

- 先重试（偶发）；连续 2–3 次失败再看网络。
- 若 curl 也超时：在 Bot 上重启 Tailscale（或重连），再测；仍不行检查 tailnet ACL 是否
  允许 8888/tcp。
- 若 curl 通但 connector 失败：重启 Bot 的 Hindsight 连接器/插件，或重新 OAuth。
- Mac Mini 侧无需改动；如需检查 macOS 防火墙：
  `sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate`
  （确认 OrbStack / 8888 入站未被阻断）。

## 6. 结论

Hindsight 服务健康，Master 侧继续按"可掉线、不阻断"设计运行；等 Bot 侧网络恢复后，
`get_bank("sherlock", ...)` 应恢复。
