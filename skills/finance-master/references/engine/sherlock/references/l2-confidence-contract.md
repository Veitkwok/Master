# L2 Confidence Contract (Cog-4)

**Owner:** Central Brain (`sherlock`)  
**Applies to:** every L2 skill that emits `### RETURN_BLOCK`  
**Relationship to conf v3.0:** L2 grades are **advisory skill-local quality**. Only the Brain emits user-facing `### CONFIDENCE_BLOCK` with `mode:` and full five dims.

Load this file when calibrating L2 grades or Brain re-grade (§H.6). L2 skills carry a **compact inline** of the same rules (do not require loading this path mid-tool if the skill body already states them).

---

## 1. Separation of duties

| Layer | Emits | Meaning |
|-------|--------|---------|
| **L2** | `confidence: A\|B\|C` (+ optional basis fields) | Quality of **this skill’s deliverable** given its inputs |
| **Brain** | `### CONFIDENCE_BLOCK` + `### CHALLENGE_NODES` | Quality of the **user-facing thesis / forecast / ranking / safety stop** under mode ceilings |

**Hard rules**

1. L2 **must not** emit `### CONFIDENCE_BLOCK` or `mode: lite|standard|max`.  
2. L2 **must not** present `confidence: A` as “buy with high confidence.”  
3. Brain **must re-grade** after every L2 RETURN before a directional user conclusion.  
4. Brain may keep L2 grade as an input log line: `L2_CONF_ADVISORY: A → BRAIN_REGRADE: B`.

---

## 2. L2 grade meaning (skill-local)

| Grade | Skill-local meaning |
|-------|---------------------|
| **A** | Deliverable complete for skill scope; material inputs present; no critical `fields_gap`; methods applied cleanly |
| **B** | Directional / usable with known gaps or thin falsification inside the skill |
| **C** | Incomplete, narrative-heavy, social-only, or critical gaps — Brain should not upgrade tone |

### Universal L2 ceilings

| Condition | Max L2 `confidence` |
|-----------|---------------------|
| `status: partial` | **B** |
| Any **material** `fields_gap` (skill cannot finish core artifact) | **B** |
| Evidence is X/social-only (no IBKR/Web primary for skill’s hard claims) | **C** |
| `status: blocked` | no investment A; use `partial`/`blocked` + C or omit thesis |
| Invented numbers / banned data path used | invalid RETURN (Brain discards grade) |

### Scope tags (`confidence_scope`)

| Scope | Typical skills |
|-------|----------------|
| `skill_local` | deep-analysis default; generic tools |
| `valuation` | company-valuation, saas-valuation-compression |
| `discovery` | x-advanced-research, serenity-skill |
| `panel` | investor-panel |
| `safety` | trap-detector |
| `sentiment` | finance-sentiment; x-adv sentiment mode |
| `single_dim` | earnings-*, sepa, options, liquidity, corr, etf, hormuz, startup, estimate |

ETF product / sleeve theses: user-facing grade is still **Brain §1.4**. Issuer factsheet/holdings/ER counts as an independent WEB chain. A research-cache digest (this pack has none) and social heat do **not**.

**Discovery / pre-deep:** even if skill-local A, Brain user ranking for undeeep names is **≤ B** (mode rule).

**Safety:** grade = confidence in **classification** (trap level), not in “XYZ is a good long.”

---

## 3. Extended RETURN_BLOCK fields (Cog-4)

Minimum (already required):

```text
confidence: A|B|C
```

**Should emit (Cog-4):**

```text
confidence: A|B|C
confidence_scope: skill_local|safety|discovery|valuation|panel|sentiment|single_dim
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: ["..."]   # empty list OK
```

Notes:

- `confidence_basis` is a **2-dim sketch**, not full conf v3.0 (Brain owns dims 1–5).  
- `data_gaps_material: true` ⇒ L2 grade **≤ B** and Brain starts ≤ B for that artifact.  
- Investor-panel **per-voter** `confidence: 0-100` stays; RETURN-level A/B/C is panel **aggregate quality**.

---

## 4. Brain re-grade algorithm (§H.6)

After validating RETURN structure:

```text
1. Parse l2.confidence, l2.confidence_scope, fields_gap, status, artifacts
2. Start candidate = l2.confidence
3. Apply floors/ceilings:
   a. status partial OR material fields_gap OR data_gaps_material → candidate ≤ B
   b. confidence_scope in {discovery} and path is pre-deep screen → candidate ≤ B
   c. X/social-only independent support for directional claim → candidate ≤ C
   d. mode_effective lite → apply §1.4 lite ceilings (default ≤ B; X-only ≤ C)
   e. Brain independent_chains for user thesis < 3 → cannot emit user grade A
   f. L2 A does not grant Brain A unless Brain dims all strong under §1.4
4. Run full §1.4 on Brain’s merged L0 + L2 artifacts → CONFIDENCE_BLOCK
5. Log: L2_CONF_ADVISORY / BRAIN_REGRADE / limiting dims
6. Emit CHALLENGE_NODES per §1.5 (L2 may suggest falsifiers in counterfactuals only)
```

### Quick decision table

| L2 conf | Material gaps | Brain chains ≥3 + dims strong | User-facing grade |
|---------|:-------------:|:-----------------------------:|-------------------|
| A | no | yes | A possible |
| A | no | no | ≤ B |
| A | yes | * | ≤ B |
| B | * | * | ≤ B (or C if thin) |
| C | * | * | ≤ C |

---

## 5. Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| L2 A + Brain copies A with no dim audit | Always re-run §1.4 |
| deep-analysis user report “confidence A” as buy | Framework zones only; Brain §10 + conf |
| serenity A on shortlist → user A ranking | Pre-deep ≤ B |
| trap conf A misread as bullish | Safety scope; hard_stop wins |
| finance-sentiment A from X-only | L2 ≤ C; Brain ≤ C for social-only thesis |

---

## 6. Examples

### Valuation tool returns A; Brain B

```text
L2 company-valuation: confidence A, fields_gap [full_segment_model]
→ data_gaps_material effectively true for IC-grade claim
→ BRAIN_REGRADE: B (limiting: falsification_rigor / gaps)
```

### Trap returns A on hard_stop

```text
L2 trap-detector: confidence A, confidence_scope safety, hard_stop true
→ Brain may use grade A for *safety classification*
→ No investment CONFIDENCE_BLOCK buy thesis; stop path
```

### Discovery returns A

```text
L2 serenity: confidence A on scored shortlist
→ Brain pre-deep table grades ≤ B
→ After deep×N, re-grade per name under §1.4
```

---

*Cog-4 · L2 advisory grades · Brain owns conf v3.0*
