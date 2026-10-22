# Research Bias Checklist · 五 bias 一页纸

**ID：** GH5 / B-P1c  
**状态：** done（文档权威）· Brain **§C.2b 已挂钩**（不粘贴全文进 skill）  
**日期：** 2026-08-11  
**来源蒸馏：** [HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading) `research-discipline`（60 秒态度重置）  
**对齐：** Sherlock §C **A2 / A5 / B2 / B5** · conf dim2 否证 · Challenge Nodes · trap  
**用途：** 任何 **Stock / ETF / 卡点/瓶颈** 研究开场 + 收尾自检；Brain 可引用本页，**不**做成第 72 个 skill  

**不是：** 新 workflow、新 conf 维度、投顾建议。

---

## 0. 何时用（30 秒）

```text
研究任务开始前 → 扫一遍五 bias
写结论 / CONFIDENCE_BLOCK 前 → 再扫一遍「否证与过期」
```

| 路径 | 必跑？ |
|------|:------:|
| 个股 deep / 买不买框架 | **是** |
| ETF 分类 / 对比 / M4–M7 机会 | **是**（尤其 narrative + recency） |
| 卡点/瓶颈扫描 | **是**（尤其 leader + English） |
| 纯报价 / 1 句事实 | 否 |

---

## 1. 五 bias + 纠正（核心表）

| # | Bias | 表现 | 纠正动作（可操作） | Sherlock / 产品挂钩 |
|---|------|------|-------------------|---------------------|
| 1 | **Leader-bias** | 搜索与注意力被大市值/头部叙事吸走；名单只剩 NVDA/AAPL/SPY 级 | 主动问：「不在 top-10 里谁该在？」；补 mid/small、供应商、替代指数；卡点/瓶颈 分层时别只写龙头 | 与 discovery / serenity 覆盖面；防「只研明星」 |
| 2 | **English-bias** | 只用英文源 → 漏掉 JP/KR/TW/EU 卡点与供应商（硬件链尤甚） | 硬件/供应链 thesis：**显式**查当地语言 IR、交易所代码、本地新闻；US ADR 不等于完整覆盖 | 产品仍 **US equities 主场**；非美标的可作 **证据辅链**，不作默认投资路径（§4） |
| 3 | **Narrative-bias** | 被标签带走（「AI 股」「高股息」「新质生产力」）而不是业务与单位经济 | 撕掉标签：产品是什么、收入来自哪、单位经济/持仓/费率；「AI」可能 **零 AI 收入** | §C **B2** 叙事污染；**A5** 信号≠证据；ETF **M1/M5** 标签诚实 |
| 4 | **Confirmation-bias** | thesis 成形后只搜支持项 | **Munger 反转**：每个多头点强制搜 bear / risks / problems；结论至少挂 **1 条否证或杀线** | §1 Step 3 否证优先；conf **dim2**；**CHALLENGE_NODES** `what_would_falsify`；§C **A2** |
| 5 | **Recency-bias** | 用排序靠前的旧数字当现状 | 关键数字 **标日期**；优先近 30 日；>1 年标 **possibly stale**；分位/费率/AUM 尤其敏感 | conf dim3 Givens；DATA_GAP 优于假新鲜；ETF 费率/政策以发行商页为准 |

**一句话总纲：** 扩覆盖（1–2）→ 撕标签（3）→ 主动打自己（4）→ 数字有保质期（5）。

---

## 2. 开场脚本（复制用）

研究开始前写一句 thesis，然后自问：

```text
Thesis（一句）: ________________________________

[ ] Leader：名单是否只有大盘/明星？补一个非明星名或供应链层
[ ] English：若 thesis 含硬件/卡点，是否查了非英文主场玩家？（US-only 投资路径另说）
[ ] Narrative：标签剥掉后，业务/持仓/费率一句话是什么？
[ ] Confirm：我准备搜的 bear 关键词是什么？
[ ] Recency：本轮最关键的 1–3 个数字，我要求 asof 吗？
```

---

## 3. 收尾脚本（写结论前）

```text
[ ] 是否至少有一条 disconfirming 证据或明确 DATA_GAP？
[ ] 是否误把 X/媒体叙事当 L0 物理事实？（B2）
[ ] 关键数字是否带日期？有无 >1y 未标注 stale？
[ ] ETF：是否用产品结构（费率/杠杆/收入机制）纠正了「主题故事」？
[ ] conf：dim2 falsification 能否写 strong？不能 → 勿装 A
```

---

## 4. Stock vs ETF 速查

| Bias | 个股怎么踩 | ETF 怎么踩 |
|------|------------|------------|
| Leader | 只看 mega-cap 同业 | 只比 SPY/QQQ，忽略同类卫星或费率更优替代 |
| English | 漏亚洲供应商 | 漏非美底层资产（若持仓有 ADR/全球）— 仍可用英文 13F/持仓表核对 |
| Narrative | 「AI 叙事股」无收入 | 「红利 / 月入 / 低波」话术；**M5** 天花板 |
| Confirm | 只搜 upside | 只搜「为什么该加仓」；忽略 tracking / 折溢价 / 政策 |
| Recency | 旧 PE、旧指引 | 旧费率、旧 AUM、旧分位线当现价便宜 |

---

## 5. 与 trap / conf 的边界

| 机制 | 管什么 | 与本页关系 |
|------|--------|------------|
| **trap-detector** | 泵砸、内幕话术、群聊保证 | 叙事热时 **先** trap；本页管日常研究偏见 |
| conf v3 dim1–5 | 证据独立性与否证质量 | 本页是 **开场/收尾习惯**；不替代 conf 块 |
| Challenge Nodes | 可证伪点 | bias #4 的落点字段 |
| thesis-memory (GH2) | 跨会话「为何买/为何错」 | 登记 thesis 时应用本清单一次 |

**不做：** 把五 bias 再做成独立 L2 skill 或强制每轮工具调用。

---

## 6. Agent 引用约定（可选）

```text
若任务为 directional 研究（个股 deep / ETF 配置或机会 / 卡点/瓶颈 扫描）：
  1. 在 Step 0 或写 Givens 前扫本页 §1（Brain 挂钩：sherlock §C.2b）
  2. 输出不必打印整表；可在 Falsification notes 或 working log 写：
     BIAS_CHECK: leader=ok|weak; narrative=ok|weak; confirm=ok|weak; recency=ok|weak
  3. 任一项 weak 不得单靠叙事给 A-grade
```

Runtime：**§C.2b + Step 0 清单已挂钩**。本页仍是展开权威，不要把全文塞进 skill boot。

---

## 7. 来源与勿照搬

| 借鉴 | 勿照搬 |
|------|--------|
| 五 bias 定义 + 60 秒清单节奏 | Vibe 整平台、外部行情源 热路径 |
| 开场/收尾两次检查 | 89 skill 全量安装 |
| 与「数字校验 / 报告审计」分层的思路 | 非美默认投资路径、A 股 ontology |

权威对照：`methodology-github-borrow-vs-skip.md` §2.2 · `github-borrow-stock-vs-etf-next.md` GH5。

---

## 8. 变更记录

| 日期 | 变更 |
|------|------|
| 2026-08-11 | GH5 初版：五 bias 一页纸 + stock/etf 速查 + agent 可选引用 |

---

*研究纪律 · 非投资建议 · 蒸馏不整仓*
