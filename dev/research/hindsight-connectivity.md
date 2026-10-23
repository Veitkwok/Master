# Hindsight 接入（2026-10-23 迁移后 · Cloudflare Tunnel）

> 旧方案（Bot ↔ Tailscale ↔ Mac Mini:8888）已弃用。当前链路用 **Cloudflare Tunnel +
> Caddy 令牌网关 + 远程 MCP（Streamable HTTP）**，Bot 侧三个连接器实测正常。
> **令牌不写入本文件、仓库或聊天**；只在 Mac Mini 的 `~/.hindsight-gate/token`（600）、
> Bot 连接器请求头、维护者电脑的副件里。

---

## 1. 链路

```text
客户端（Grok Bot 连接器 / 其他 MCP 客户端）
  → https://hindsight.veitkwok.us.kg/mcp/<bank>/     （请求头 X-Hindsight-Token）
  → Cloudflare 边缘
  → Cloudflare Tunnel（Mac Mini 上的 cloudflared 主动外连；家里不开端口）
  → Caddy 令牌网关 127.0.0.1:8889（校验请求头，不对返回 401）
  → Hindsight 127.0.0.1:8888（OrbStack 容器）
```

`<bank>`：`hermes`、`sherlock`、`sissyfication`。Master 只用 **sherlock**。

## 2. Mac Mini 组件

| 组件 | 位置 / 说明 |
|------|-------------|
| cloudflared | Homebrew；隧道名 `hindsight`；配置 `~/.cloudflared/config.yml`；DNS CNAME `hindsight.veitkwok.us.kg`；`flush_interval -1` 用于 SSE |
| Caddy 网关 | `~/.hindsight-gate/Caddyfile`，监听 `http://:8889`（**必须写 `:8889`，不能写 `127.0.0.1:8889`**，否则 Host 不匹配会返回空 200）；令牌文件 `~/.hindsight-gate/token`（600） |
| 自启 | launchd：`com.veit.hindsight-gate`、`com.veit.cloudflared-hindsight`（RunAtLoad + KeepAlive） |
| 重启 | `launchctl kickstart -k gui/$(id -u)/com.veit.hindsight-gate`（另一个换服务名） |

前置条件：**Mac Mini 必须开机，cloudflared 与 Caddy 进程在跑**。

## 3. Bot 连接器

| 连接器 | bank | 用途 |
|--------|------|------|
| `hindsight-sherlock-cf` | sherlock | **Master 唯一使用**（读 recall + 写 sync_retain） |
| `hindsight-cf` | hermes | 其他 agent 用；Master 不写 |
| `hindsight-sissyfication-cf` | sissyfication | 无关项目；不碰 |

工具（实测）：`get_bank`（看库/状态）、`recall`（读）、`sync_retain`（写）。
没有 `list_banks`；列 bank 用 HTTP `GET /v1/default/banks`（带令牌）。

## 4. 验证

```bash
# 不带令牌 → 401
curl -s -o /dev/null -w '%{http_code}\n' https://hindsight.veitkwok.us.kg/health

# 带令牌 → {"status":"healthy",...}
curl -s -H "X-Hindsight-Token: $HINDSIGHT_TOKEN" https://hindsight.veitkwok.us.kg/health

# 列 bank
curl -s -H "X-Hindsight-Token: $HINDSIGHT_TOKEN" https://hindsight.veitkwok.us.kg/v1/default/banks
```

Bot 侧也可以直接让连接器 `get_bank("sherlock")`；返回正常即通。

## 5. 失败判断

| 现象 | 含义 | 处理 |
|------|------|------|
| 401 | 令牌/请求头不对 | 更新 Bot 连接器请求头；核对 Mac 的 token 文件 |
| 502 / 521 / 1033 | cloudflared 隧道断 / 边缘连不上 | Mac Mini 上 `launchctl kickstart` 重启 cloudflared；看 `~/.cloudflared` 日志 |
| 连接超时 | Mac Mini 离线 / 断网 / 睡眠 | 唤醒机器，确认隧道进程 |
| connector 报工具不存在 | 连错 bank/连接器 | 确认用 `hindsight-sherlock-cf` |

失败一律按 `hindsight: down` 处理：重试 1 次，然后继续本轮分析，卡片标
`memory: missing`——**不阻断**。

## 6. 安全与运维

- 令牌只存三处（Mac 文件 600、Bot 连接器请求头、维护者副件）；换令牌 = 改 Caddyfile +
  重启网关 + 更新三个连接器请求头。
- 可选再加 Cloudflare Access Service Token（客户端多带 `CF-Access-*` 头）。
- Hindsight 只监听本机端口，外部唯一入口是隧道域名。
- 旧 Tailscale 节点 `grok-bot-vm-1` / `grok-bot-vm` 已 offline，可在 Tailscale
  管理后台删除；新 Bot 节点为 `grok-bot-vm-2`。
