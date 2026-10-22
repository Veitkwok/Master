# 分析引擎（vendored finance-master 4.6.8）

> **这不是技能。** 本目录是 `finance-master` 技能内部的参考引擎：
> 所有 `GUIDE.md` 都是**方法文档**，不是可独立触发的 skill，不要把它们注册或平铺。
> 唯一入口是技能根目录的 `SKILL.md`。

---

## 1. 来源与版本

| 项 | 值 |
|----|----|
| 上游 | `finance-master-skill-build/skills/finance-master/`（skill 4.6.8，etf v0.4.0） |
| 来源副本 | 2026-10-22 的 Master 迁移稿（已含 22 文件运行时边界修改） |
| 本包版本 | pack 1.0.0 / engine 4.6.8 |
| 冻结日期 | 2026-10-23 |
| 结构变化 | 20 个 `SKILL.md` → `GUIDE.md`（防被技能系统注册）；去掉 L0 副本、README 存根、serenity assets/evals/examples、x-adv 85 号名单与 mover 文件 |

---

## 2. 目录地图

```text
engine/
├── sherlock/                         # 中央脑（道）
│   ├── GUIDE.md                      # §0–§11、§1.4 置信度、§1.5 证伪、§8.3、§9.4
│   └── references/
│       ├── full-engine.md            # 完整引擎 §C/§1/§M/§H/§6/§10/§13
│       ├── l2-confidence-contract.md # L2 advisory → Brain re-grade
│       ├── confidence-examples.md    # 置信度正反例
│       ├── data-pack-schema.md       # Brain 侧 DATA_PACK 规范
│       ├── banned-patterns.yaml      # 禁用工具/模式
│       └── method-library/           # M01–M12（按需单卡加载）
├── modules/                          # 术（20 个方法模块，按需读）
│   ├── company-valuation/            # 目标价数字源（DCF/可比/SOTP）
│   ├── trap-detector/                # 八信号 → trap_level
│   ├── etf/                          # M1–M7 产品方法
│   ├── deep-analysis/                # 点名深研
│   ├── investor-panel/               # 点名评审团
│   ├── serenity/                     # 点名卡点/瓶颈扫描
│   ├── x-advanced-research/          # X 手艺（重写版）
│   ├── earnings-preview/ · earnings-recap/ · estimate-analysis/
│   ├── sepa-strategy/ · stock-liquidity/ · stock-correlation/ · etf-premium/
│   ├── options-payoff/ · saas-valuation-compression/ · startup-analysis/ · hormuz-strait/
│   └── …
└── docs/reference/                   # 引擎会打开的方法笔记
    ├── priced-in-checklist.md
    ├── research-bias-checklist.md
    └── methodology-metric-and-bands.md
```

---

## 3. 路径约定

- 引擎文件**内部**引用（`references/xxx.md`）是相对**该文件自身所在目录**的。
- 技能入口 / runbooks / contracts / decisions 里的路径是相对**技能根目录**的。
- 不要在本目录新增 `SKILL.md`（只允许技能根一个）。
- 引擎不引用包外路径；不引用旧 monorepo 的 `cache/`、`lists/`、`scripts/`。

---

## 4. 运行时边界补丁（白名单）

相对上游 4.6.8，本引擎只在**运行时边界**改过句子，方法核心未动。补丁类别：

| # | 类别 | 例子 |
|---|------|------|
| 1 | 默认模式 | lite → standard（Master routine 场景） |
| 2 | 无 cache | `cache/` 步骤 → `CACHE_MISS` / 不创建缓存 |
| 3 | 记忆动作 | 本机 HTTP 记忆 → Bot Hindsight bank `sherlock` |
| 4 | 账户读取 | 允许读持仓/余额；禁止下单/草稿（除非用户要求） |
| 5 | 建议卡出口 | "禁止该买"/§8.3 观察卡 → 入口 advice-card 契约 |
| 6 | 旧发现链 | KOL routine 不启动 x-adv→serenity→deep DAG |
| 7 | 路径根 | 旧 `Master/…` / `skills/finance-master/…` → 技能内相对路径 |
| 8 | 工具名 | Grok Build/IBKR 旧工具名 → 能力名（连接器运行时发现） |
| 9 | 旧站点 | Balder/Serenity/Koltracker 网站、x-adv 85 号名单 → 删除 |
| 10 | 资金口径 | 历史 $1000 上限 → 用户当轮说现金才写金额 |
| 11 | ETF/财报口径 | "research only" → "no auto-order; stance 在建议卡" |

补丁共约 49 处句子 + 42 处路径 + 74 处工具名（见
`dev/vendor/normalize_engine.py` 的清单）。修改规则：**只允许**改运行时边界句；
若必须改方法正文，先在本 README 登记、并在 `dev/hash-manifest.json` 里更新方法核 hash。

### 40 个与上游不同的文件

改动分三类：GUIDE 改名（20）、路径/工具名归一（18）、内容补丁（2：x-adv 三件重写、
serenity/etf/earnings 等口径句）。完整清单可用
`python3 dev/vendor/diff_engine.py`（）或 `git diff` 查看。

---

## 5. 方法核（冻结，非必要不改）

以下内容视为"道"，改动必须单独评审：

- `sherlock/GUIDE.md`：§C.1 反模式、§1.4 五维置信度、§1.5 Challenge Nodes、
  §1.3 推理层、§8.L 文风、§H.6 re-grade。
- `sherlock/references/full-engine.md`：§C、§1 Steps 0–5、§M、§H、§6、§10、§13。
- `sherlock/references/l2-confidence-contract.md` 主体。
- `sherlock/references/method-library/M01–M12`。
- `modules/company-valuation/references/{dcf,relative_valuation,sotp,wacc_erp_rates}.md`。
- `modules/trap-detector/references/eight-signals.md`。
- `modules/etf/references/modules/m1–m7*` 的方法体（页脚口径除外）。
- `docs/reference/priced-in-checklist.md`。

---

## 6. 加载规则（省 token）

| 场景 | 读 |
|------|----|
| routine 分析（worker） | 脚本自动拼固定清单（sherlock GUIDE + full-engine + 估值 + trap + priced-in + book），Bot 不用逐本读 |
| routine 分析（inline 回退） | 同上，Bot 逐本读一次；同轮不重复读 |
| ad-hoc 深研 | + `modules/deep-analysis/GUIDE.md` + 其 references（按 intent） |
| ETF | + `modules/etf/GUIDE.md` + 对应 M1–M7（逐个，不一次全读） |
| 卡点/评审团 | + `modules/serenity` 或 `modules/investor-panel` 对应文件 |
| 财报 | 只读 preview 或 recap 一份 |
| 期权/SaaS/创业/宏观 | 只读对应单模块 GUIDE |

禁止：整库加载、一次读多个方法库卡片、读 README/evals/examples。

---

## 7. 同步上游（升级流程）

1. 在 monorepo 更新 `skills/finance-master`；
2. 按 `dev/vendor/` 的流程重新拷贝 + 运行 `normalize_engine.py`；
3. `git diff` 审阅：只允许出现运行时边界改动；
4. 更新 `dev/hash-manifest.json`、本 README 的补丁计数与版本；
5. 跑 `dev/check_pack.py`。

---

## 8. 已知残留

- 个别模块 `GUIDE.md` 的 `related_skills` 元数据仍写着旧模块名（仅元数据，无害）。
- `deep-analysis/references` 中有历史脚本时代的注释（方法仍有效，执行方式已改为
  Bot/worker 直接推理，不再跑 Python 抓取脚本）。
- `etf` 模块的部分历史说明（evals、watchlist 文件）保留为方法备注，不参与运行。

---

*vendored engine · 4.6.8 · 2026-10-23 · 方法核冻结 · 只改运行时边界*
