---
name: investor-panel
description: >
  US equity investor panel (36 frameworks / Top-10).
  Brain-invoke only (sherlock INVOKE); do not trigger from casual user chat.
  finance-master v4.6.8.
version: 4.6.8
ecosystem: 4.6.8
author: FloatFu-true (original) / Veit Kwok (v4.5 US-only)
license: MIT
metadata:
  tags: [finance, us-stocks, investor-panel, voting, value-investing, growth-investing]
  market_scope: US_EQUITIES_ONLY
  role: L2_PANEL
  related_skills:
    - sherlock
    - deep-analysis
---

# Investor Panel · v4.6.8 (US only)

> **L2 skill.** Invoked by Central Brain (`sherlock`). Do **not** call other L2 skills.  
> **Market:** US equities only. China A-share 游资 / 中国价投 paths are **quarantined**.

---

## Consumer rules

1. Use Brain **`data_pack`** + any prior deep-analysis artifacts first.  
2. Do **not** re-pull full price/history if pack already has quote + technicals.  
3. Fill gaps with Web (and IBKR only if Brain `budget.may_fetch` allows).  
4. **Never** load:
   - `group-e-china-value` / `group-f-china-youzi` (quarantined)
   - `lhb-analyzer` / seat-encyclopedia 游资射程  
5. Emit **`### RETURN_BLOCK`** for the Brain.

---

## Inputs (expected)

| Field | Source |
|-------|--------|
| ticker, name, industry, mcap | Data Pack / Web |
| ROE, PE, PB, margins, growth, FCF | fundamentals_web |
| Stage / MAs / RSI / distance from high | ohlcv summary |
| Valuation vs history / peers | pack or Web |
| Moat notes | prior analysis |
| Catalysts / events | Web |
| Sentiment | optional X summary |

If critical inputs missing → `status: partial`, confidence ceiling **C** for those voters.

---

## Panel modes

| Mode | When | Who |
|------|------|-----|
| **US-36 (default for “完整评审团”)** | User asks full panel / Brain requests full | `../deep-analysis/references/investor-frameworks.md` (~36 US names) |
| **US-lite (default otherwise)** | “快速评审” / token save / Brain budget tight | Live groups **A, B, C, D, G, I** only (~24 seats in refs) |
| **Named subset** | “巴菲特会怎么看” | Single methodology from frameworks |

**Removed from live routing:** 65-person multi-market set, Group E (中国价投), Group F (游资).

---

## Per-investor output shape

```text
investor_id: buffett
name: 巴菲特
group: A|B|C|D|G|I|FRAMEWORK
signal: bullish|neutral|bearish
confidence: 0-100
score: 0-100
verdict: 强烈买入|买入|关注|观望|等待|回避|不达标|不适用
reasoning: 1-3 sentences with numbers
comment: 1-2 sentences in-voice
pass: [...]
fail: [...]
ideal_price: number|null
period: holding horizon note
```

**Confidence calibration**
- 85–100: hard rules clear hit/miss  
- 60–84: mostly aligned  
- 30–59: mixed / wait  
- 0–29: method N/A or data insufficient → prefer `signal: neutral`, `verdict: 不适用`

---

## Execution steps

### Step 1 · Scope
- Confirm US ticker (refuse pure A-share LHB-style requests).  
- Choose US-36 vs US-lite per mode table.  
- Load:
  - US-36 → `../deep-analysis/references/investor-frameworks.md`
  - US-lite → `references/group-a-classic-value.md` … `group-d-technical.md`, `group-g-quant.md`, `group-i-serenity.md`  
- Optional voice: `references/quotes-knowledge-base.md`, `references/serenity-voice.md`

### Step 2 · Vote
For each investor in scope:
1. Extract metrics their method cares about  
2. Apply **their** rules (do not average into bland consensus early)  
3. Write `comment` in-character (Buffett “we”, Munger inversion, Wood S-curve, Serenity bottleneck language, etc.)  
4. Mark `不适用` when method truly does not apply (e.g. deep-value screens on pre-profit hypergrowth) without fake precision  

### Step 3 · Aggregate
- `panel_consensus` = % bullish (exclude pure 不适用 if noted)  
- `vote_distribution` by verdict  
- `signal_distribution` bullish / neutral / bearish  
- Optional **Great Divide**: highest-conviction bull vs bear, 3 numbered clash points  

### Step 4 · RETURN_BLOCK

```text

## L2 confidence (Cog-4 · advisory only)

`confidence` in `### RETURN_BLOCK` is **skill-local deliverable quality**, not user investment confidence.

| Rule | Max grade |
|------|-----------|
| `status: partial` or material `fields_gap` | **B** |
| X/social-only evidence for hard claims | **C** |
| `status: blocked` | no thesis A |
| Complete skill scope + hard sources + no material gaps | **A** allowed (still advisory) |

Default `confidence_scope` for this skill: **panel**.

Per-investor `confidence: 0-100` is **method fit**, not Brain grade. RETURN-level A/B/C = quality of the **aggregate panel package**. Votes show disagreement; they do not auto-set user CONFIDENCE_BLOCK.

Also emit Cog-4 fields when practical: `confidence_scope`, `confidence_basis` (evidence_independence, physical_mechanical, data_gaps_material), `limiting_factors`.

**Never** emit Brain `### CONFIDENCE_BLOCK` or `mode:` — the Central Brain re-grades via §H.6.

### RETURN_BLOCK
skill: investor-panel
status: ok|partial
ticker: SYM
confidence: A|B|C
confidence_scope: panel
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [votes, consensus]
fields_gap: [...]
artifacts:
  mode: us36|us_lite|subset
  panel_consensus: 0.xx
  signal_distribution: {bullish, neutral, bearish}
  top_bull: {name, score, one_liner}
  top_bear: {name, score, one_liner}
  votes: [ ... compact list ... ]
counterfactuals: []
raw_notes: <≤400 words>
```

---

## Live reference groups (US)

| Group | File | Role |
|-------|------|------|
| A Classic value | `references/group-a-classic-value.md` | Global methods, US names |
| B Growth | `references/group-b-growth.md` | |
| C Macro hedge | `references/group-c-macro-hedge.md` | |
| D Technical | `references/group-d-technical.md` | |
| G Quant | `references/group-g-quant.md` | |
| I Serenity | `references/group-i-serenity.md` | Bottleneck / structure |
| US-36 table | `../deep-analysis/references/investor-frameworks.md` | Canonical full US set |

### Quarantined (do not load)

| Former | Location |
|--------|----------|
| E 中国价投 | **banned** — not in product tree |
| F 游资 | **banned** — not in product tree |
| LHB / seats | **banned** (`lhb-analyzer`) |

---

## Style guardrails

| Voice | Do |
|-------|-----|
| Buffett | Moat, owner earnings, “we”; no PE>40 “buy” without exceptional case honesty |
| Munger | Inversion, psychology; blunt |
| Lynch | Story + PEG; no PEG on zero EPS |
| Wood | Disruption / S-curve; not for legacy no-growth |
| Serenity | Scarce layer, evidence, failure modes |
| 段永平 (if in frameworks) | 三对 / business quality; plain language |

**Forbidden:** empty “基本面良好”; fake 游资 seat drama on US names.

---

*v4.6.8 · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only*
