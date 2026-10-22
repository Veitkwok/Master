# X 输出模板（给技能入口）

## 1. 用户可见摘要（routine）

```text
## X 扫描 · primary_babybus · 2026-10-23 07:32 +08
读取：1 次时间线（@BabybusFL，14 天窗），12 条 → 保留 8 条，3 只票
- $NVDA：作者称"下季数据中心订单可见度提升"（原句，2026-10-21，link）→ 候选
- $MRVL：仅出现代码，无论述（2026-10-22，link）→ 观察
- $PLTR：非美股/无关，丢弃
data_gap：无
```

## 2. 交给技能入口的候选块

```text
X_CANDIDATES:
  routine: primary_babybus
  window: 2026-10-09..2026-10-23
  reads: 1
  posts_kept: 8
  candidates:
    - symbol: NVDA
      source: primary
      handles: [BabybusFL]
      mentions_14d: 1
      accounts_14d: 1
      conviction_hint: high
      quotes:
        - handle: BabybusFL
          url: https://x.com/...
          posted_at: 2026-10-21T13:05:00Z
          line: "下季数据中心订单可见度提升，guide 可能上修"
      risk_flags: []
    - symbol: MRVL
      source: primary
      conviction_hint: low
      quotes: [...]
  dropped: [PLTR(非美股), ...]
  source_error: []
```

## 3. 规则

- `candidates` ≤15，按"机制/数字/时间窗 → 多账号 → 补充号"排序。
- 每条候选至少 1 条带链接的原句；无原句的不进候选，只进观察。
- 不写 stance、不写目标价、不写仓位。
