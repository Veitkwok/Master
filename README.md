# Finance Master · Grok Bot 包（Master v1）

一套给 **xAI Grok Bot** 用的美股 / ETF 研究技能包：KOL routine 选股 → 引擎分析
（Sherlock 置信度 + 估值 + 陷阱）→ IBKR / Schwab 持仓对照 → **买入 / 目标价 / 卖出建议卡**。

- **一个技能入口**：`skills/finance-master/`（SKILL.md + references）
- **冻结引擎**：`skills/finance-master/references/engine/`（Sherlock 4.6.8，方法核不改）
- **不做的事**：不自动下单、不写嘉信、不保证收益、不编数字。

---

## 1. 安装（Grok Bot 电脑）

推荐：把本仓库放到 Bot 能访问的 HTTPS 位置（私有 GitHub 等），在 Bot 终端：

```bash
git clone https://github.com/Veitkwok/Master.git /workspace/master
cd /workspace/master
bash install.sh
```

`install.sh` 做三件事：

1. 复制 `skills/finance-master/` → `~/agent-data/workflows/finance-master/`（技能库）；
2. 创建 `/workspace/master/state/`（运行状态）与 `out/`（输出）；
3. 打印 `verify.sh` 自检结果。

更新：

```bash
cd /workspace/master && git pull && bash install.sh
```

> 如果 Bot 的社区文件安装路径失效：routine prompt 里直接写
> "读取 `/workspace/master/skills/finance-master/SKILL.md` 并按它执行" 也能工作
> （技能库只是让 `/` 菜单可触发）。

---

## 2. 配置 routine（一次性）

1. 打开 Bot → Routines，按 `runtime/routine-setup.md` 建 **5 类 routine**（主账号 3 个 +
   补充 1 个 + 持仓复核 1 个；若一天两轮，复制对应 routine 并改时间）。
2. 每个 routine prompt 用 `runtime/routine-setup.md` 里的模板（很短，流程在技能里）。
3. 时区设 `Asia/Shanghai`。
4. Approvals：参考 `skills/finance-master/references/runtime/approvals.md`：
   - Auto Review；
   - Ask first：下单/草稿、watchlist 写、邮件、发布；
   - 如支持，自动放行 `python3 .../deepseek_analyze.py`。
5. DeepSeek key（二选一）：
   ```bash
   echo '<key>' > /workspace/master/.secrets/deepseek.key && chmod 600 /workspace/master/.secrets/deepseek.key
   # 或 Bot secret 环境变量 DEEPSEEK_API_KEY
   ```
   然后按 `runtime/routine-setup.md` §2 **预放行固定命令**（这一步不做，routine 可能被审批拦）。

---

## 3. 首次自检

```bash
bash verify.sh
python3 dev/check_pack.py            # 结构/路径/禁词/大小/方法核 hash
```

在 Bot 对话里说：

```text
按 finance-master 技能，读一次我的 IBKR 持仓，告诉我读到几只、有哪些 watchlist。
```

能读出来 → 连接器就绪；读不到 → 先排查 IBKR 连接，再跑 routine。

---

## 4. 日常使用

| 你说 | 发生什么 |
|------|----------|
| （定时）KOL routine | 读账号 → 选票 → 分析 → 出卡 |
| （定时）持仓复核 | 全部持仓逐仓给持有/减/卖 + 触发原因 |
| "帮我看看 NVDA" | ad-hoc 标准分析，出卡（买入/目标价/卖出） |
| "深度分析 NVDA" | deep 档（worker pro + 深研模块） |
| "记录一下：NVDA 我买了" | 写 Hindsight postmortem |
| "确认写入 NVDA" | 追加到 IBKR Candidates（仅此场景写 watchlist） |

卡上永远有 `未下单`；Schwab 仓永远"只读、需你手动"。

---

## 5. 结构

```text
Master/
├── skills/finance-master/          # 唯一安装单元
│   ├── SKILL.md                    # 入口（先读这一页）
│   ├── scripts/                    # DeepSeek worker + 自检
│   └── references/
│       ├── runbooks/               # 5 条流程
│       ├── runtime/                # 能力/状态/审批/交付
│       ├── contracts/              # 数据包/建议卡/置信度/记忆/DeepSeek/账号/账本
│       ├── decisions/              # stance/target/sell/risk gates
│       └── engine/                 # 冻结的 finance-master 4.6.8 方法库
├── runtime/routine-setup.md        # routine 粘贴文本 + 排期
├── install.sh · verify.sh
├── dev/                            # 本地校验/测试/研究（不上 Bot）
├── VERSION · CHANGELOG.md · ARCHITECTURE.md
```

---

## 6. 故障排查

| 现象 | 处理 |
|------|------|
| routine 没有产物 | 看 Bot 聊天里的失败摘要；检查 X / IBKR 连接 |
| 卡上目标价缺失 | 数据包缺财务输入（fundamentals）；本轮只能观望，下轮补 |
| 全是"观望" | 检查是否 IBKR/X/DeepSeek 全挂；检查 confidence 是否被 ceiling 压到 C |
| DeepSeek 未被调用 | 密钥缺失 → bot-inline；审批拦截 → 该 run 失败、下轮补（不是脚本异常），见 approvals.md 与 routine-setup §2 |
| IBKR 读不到 | 重新授权连接器；期间只出观察/持仓列表 |
| Hindsight 掉线 | 正常，跳过记忆继续 |
| 技能不出现 | 重跑 install.sh；或让 routine 直接读 `/workspace/master/skills/finance-master/SKILL.md` |

---

## 7. 版本

- pack `1.0.0`（见 `VERSION`）
- engine `4.6.8`（Sherlock 原版；方法核冻结）
- 变更记录：`CHANGELOG.md`
