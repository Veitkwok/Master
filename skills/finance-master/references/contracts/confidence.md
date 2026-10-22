# 置信度契约（CONFIDENCE_BLOCK · 灵魂层）

> **这是全包不可简化的一层。** 定义不在这里重写——原文在引擎里，本文件只规定
> "谁执行、怎么校验、怎么展示、什么情况下必须降级"。
>
> 权威定义：
> - 五维 / weakest-dim / 独立链 / 模式 ceiling / A/B/C：
>   `references/engine/sherlock/GUIDE.md` §1.4
> - Challenge Nodes（证伪节点）：同文件 §1.5
> - L2 advisory 与 Brain re-grade：`references/engine/sherlock/references/l2-confidence-contract.md`
> - 正反例：`references/engine/sherlock/references/confidence-examples.md`
> - 完整引擎中的 post-condition 清单：`references/engine/sherlock/references/full-engine.md` §H.4

---

## 1. 谁计算、谁校验

| 角色 | 职责 |
|------|------|
| **DeepSeek worker（默认）** | 按引擎原文计算五维、给出 `grade`、`limiting`、`independent_chains`、`CHALLENGE_NODES` |
| **Bot（仲裁）** | 结构校验 + 执行 ceiling（只降不升）+ 拒绝非法卡；**不重新打分** |
| **Bot inline（回退）** | worker 不可用时，Bot 按引擎原文自行计算，格式与 worker 相同 |

Bot 从不在没有 `CONFIDENCE_BLOCK` 的情况下给方向性结论（买入/加仓/减仓/卖出/持有）。

---

## 2. 每票必须有（原格式，不得改字段名）

```text
### CONFIDENCE_BLOCK
grade: A|B|C
mode: standard|max
dims:
  evidence_independence: strong|weak|gap
  falsification_rigor: strong|weak|gap
  assumption_audit: strong|weak|gap
  physical_mechanical: strong|weak|gap
  layer_integrity: strong|weak|gap
limiting: [...]
verification_density: "<1-2 句>"
independent_chains: ["IBKR:...", "WEB:...", "X?:..."]

### CHALLENGE_NODES
- id: CN1
  layer: L2|L3|assumption|conf_dim
  claim: "..."
  assumption: "..."
  what_would_falsify: "可观测指标 + 窗口"
  conf_dim_link: evidence_independence|falsification_rigor|...|null
```

`what_would_falsify` 必须是**可观测**的（价格/文件/事件/日期窗口），不能写
"如果情况变差"这类空话；它同时是建议卡 `invalidation` 的候选来源。

---

## 3. Bot 必须执行的 ceiling（从引擎规则抽取，只降不升）

| 条件 | 上限 |
|------|------|
| 纯 X / 社交单一来源，无 IBKR、无一手文件 | **≤ C** |
| X 整体最多算 1 条独立链（永远） | 不能靠多账号刷成 A |
| 关键数据缺失（无现价/无财务/无持仓）且无法补 | **≤ B**（重大缺口可 ≤ C） |
| 本轮为 discover 阶段、未做深研 | **≤ B** |
| A 级 | 需 ≥3 条独立链 + `assumption_audit: strong` + 证伪已做 |
| worker 返回 `status: partial` 或 `fields_gap` 影响结论 | **≤ B** |
| 建议卡要写"买入" | 至少 **B** |

优先级：**trap 橙/红 > 数据缺失 > ceiling > 研究结论**。trap 橙红时即使 A 级也
不给买点（结论只能回避 / 减持评估）。

---

## 4. 展示规则（用户看到的）

建议卡上：

```text
confidence: B
limiting: [无一手文件, X 仅 1 链]
falsify: 下季指引下调 | 连续 3 日收盘 < 50 日线
```

- 只显示 A/B/C，不显示 0–100 分、"高/中/低"第二套刻度。
- `limiting` 必须至少显示一条（若为空说明没有缺口，写 "none"）。
- 卡上的 `evidence` 行写独立链数量与类型，例如 `chains: IBKR+WEB (2)`。

---

## 5. 必须拒绝的卡（Bot 校验清单）

- [ ] 没有 `CONFIDENCE_BLOCK` 或没有 `CHALLENGE_NODES`；
- [ ] grade 超出 ceiling（例如纯 X 却给 A/B）；
- [ ] `what_would_falsify` 不可观测；
- [ ] 买入但 grade = C；
- [ ] 买入但没有 invalidation；
- [ ] trap 橙/红仍给买入；
- [ ] 用 L2 的 `confidence` 直接冒充 Brain grade（必须 re-grade）；
- [ ] `analysis_source` 与卡上证据来源矛盾。

校验失败 → 降级处理：能补则重跑一次 worker；否则卡改"观望"，摘要写明原因。

---

## 6. 与建议卡字段的对应

| 卡字段 | 来源 |
|--------|------|
| `confidence` | `CONFIDENCE_BLOCK.grade`（经 ceiling 后） |
| `limiting` | `CONFIDENCE_BLOCK.limiting` |
| `invalidation` | 优先 `CHALLENGE_NODES[].what_would_falsify`；价格失效见 `decisions/sell.md` |
| `evidence` | `independent_chains` 数量与类型 |
| `thesis` | `CHALLENGE_NODES[].claim` 对应的论点一句话 |

---

## 7. 红线

- **不得改写、简化或另造**五维定义、A/B/C 判据、独立链目录、模式 ceiling。
- 不得因为"用户想看买入"而抬高 grade；不得把 memory / KOL / heat 当独立链。
- 不得用第二套置信度刻度替代 A/B/C。
- 升级引擎版本时必须同步重验本契约（`dev/check_pack.py` 校验引用完整性）。

---

*confidence contract v1 · 原文在引擎 §1.4/§1.5 · Bot 只降不升*
