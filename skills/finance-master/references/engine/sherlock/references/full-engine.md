# Sherlock full engine (standard / max only)

Not a skill. Do not load in lite.
READ only when `mode_effective ≥ standard`.
Conf dims and §9.1 tree are not forked — dims live in `SKILL.md` §1.4; tree lives here verbatim.
INVOKE / RETURN full schemas live here (§H.1–H.5). Brain re-grade stays in `SKILL.md` §H.6.
lite must not READ this file.

After upgrade this turn (`mode_profile` → `mode_effective ≥ standard`): READ this file before Steps 1–5 / INVOKE deep / §10.

---

## §C.2 / §C.2b / §C.3 (honesty, bias hook, step matrix)

### C.2 Epistemic honesty (B-series)

| Code | Rule |
|------|------|
| **B1** | Admit ignorance cleanly; name unknowns |
| **B2** | Flag narrative/emotional pollution; raise skepticism |
| **B3** | Treat user challenges as valuable; update when valid |
| **B4** | Report degradation / overload; simplify or request data |
| **B5** | Treat known bias as calibration data |
| **B6** | Accept rigor costs; do not fake instant deep analysis |

**Example:** `A1 triggered: missing distributor inventory. Grade C.`

### C.2b Research-bias scan (GH5 · hook only)

Full page: `../../docs/reference/research-bias-checklist.md` — **do not** paste it.  
**When:** deep / etf sleeve (M4–M7) / Serenity. **Skip:** quote-only / one-fact.  
Scan at Step 0 and again before `CONFIDENCE_BLOCK`. No new A-codes — map onto existing:

| Bias | Hook | One-line action |
|------|------|-----------------|
| Leader | B5 | Is the list only mega-caps / QQQ-NVDA? Who is missing? |
| Narrative | B2 / A5 | Strip the tag; name revenue, holdings, or ER |
| Confirmation | A2 + dim2 | At least one kill / disconfirm |
| Recency | dim3 / DATA_GAP | Date every material number (`asof`) |
| English | §4 | Non-US sources = evidence only; not a default invest path |

§C **overrides** any desire for A-grade tone or completed narrative.

### C.3 Constraint × engine step matrix (Cog-2)

| Step | Must consider |
|------|----------------|
| **0** | B4 (capacity), B5 (bias in attic filter), A5 (reject signaling as L0 “proof”) |
| **1–2** | A2 (thesis not steering hyps), A5, B1 (name unknowns early) |
| **3** | A1, A3 (elevate physical risk), A2 |
| **4** | A1, B1 (conf ceilings), dim legality |
| **5 / §8** | A4 (clinical), B2 (pollution flag), B3 (Challenge Nodes / Watson) |
| **§11 follow-up** | A2 re-derive + invalidation_stack; B3 on user contest |

---

## §D.3 Attic · §D.4 Packs · §D.6 Macro

### D.3 Brain Attic source tiers (Step 0)

| Tier | Sources | Role |
|------|---------|------|
| **A** | IBKR market; SEC/IR primary; Form 4 / 13F (Web); **ETF issuer factsheet / holdings / ER** | May build independent conf chains |
| **B** | Transcripts, reputable news | Support |
| **C** | X posts | Lead-gen / heat / trap language; **≤1 independent chain**; never sole A-grade |
| **Deprioritize** | Sell-side fluff, ESG signaling, uncited blogs | Attic reject unless user forces |

### D.4 Packs (canonical)

Kinds: `DATA_PACK.QUOTE` · `INTRADAY` · `SWING` · `DEEP`.

**Full field schema:** `data-pack-schema.md` (load when building or validating a pack).

| Kind | Minimum |
|------|---------|
| `QUOTE` | `contract_id?`, `quote.last`, `asof` |
| `INTRADAY` | QUOTE + short `ohlcv` (5m and/or 1d) + optional `social_x` |
| `SWING` | QUOTE + daily structure + preferred `catalysts_web`; **ETF → `issuer` or explicit `gaps`** |
| `DEEP` | SWING + `fundamentals_web` core + preferred peers + explicit `gaps[]`; **ETF → same `issuer` rule** |

Envelope always: `kind`, `asof`, `mode_effective`, `ticker`, `ibkr_available`, `sources_used`, `gaps`.  
**Consumer contract:** `budget.may_fetch` omitted or `false` = do not re-fetch keys already in the pack. Missing key → `DATA_GAP` / `fields_gap`. Fetch only if `may_fetch: true`.

### D.6 Macro for §6

VIX / Fed week / DXY / name liquidity via §D only.

---

## §1 Enhanced reasoning engine (Steps 0–5 · single protocol)

**One engine only** for non-trivial analysis. Do not run a second parallel protocol.

### Step 0 · Pre-observation + Brain Attic + **path checklists**

**Before any L1+ inference** set `step0_complete=false` → complete checklist → `step0_complete=true`.

1. **Attic filter** — Tier A/B; Tier C X only if social/discovery/trap/lite sentiment.  
2. **Observation pass (bind §D)** per mode checklist below.  
3. **Log L0 only** — `fact + source: IBKR|WEB|X`.  
4. **Independence plan** — intended chains for conf dim1.

#### Step 0 · Outside-RTH / empty-session snapshot rule (mandatory)

When `IBKR 现价快照` returns **empty or zero** session fields (`open`/`high`/`low`/`volume`, or session range) — common **outside RTH** or when `last.is_close: true`:

1. **Do not treat the name as unpriceable.** Keep usable snapshot fields: `last`, `bid`/`ask` when present, `misc_statistics` / 52w / ADV / IV proxies.  
2. **Prefer history for structure:** call `IBKR 历史K线` (daily and/or `FIVE_MINS` for prior RTH) and bind OHLCV from bars into L0 + DATA_PACK `ohlcv.*`.  
3. Label L0 clearly: e.g. `session OHLC unavailable outside RTH; structure from history bars (source: IBKR)`.  
4. Still run the mode checklist below; mark session-only rows as **DATA_GAP** only if history also fails — never invent OHLC.  
5. Packs: `INTRADAY` / `SWING` / `DEEP` may use prior-session or multi-day history as the market skeleton; note `asof` from the latest bar or `last` timestamp.

Pilot evidence: outside RTH, snapshot session OHLC/volume can be empty while `last` + misc + history remain usable.

#### Step 0 checklists by mode_effective

| Checklist item | lite | standard | max |
|----------------|:----:|:--------:|:---:|
| `CACHE_MISS` from §0.2b (this pack has no cache files) | ✓ | ✓ | ✓ |
| Resolve `contract_id` (SESSION_CACHE/IBKR) | ✓ | ✓ | ✓ |
| IBKR snapshot (last, range, volume, ADV if avail) | ✓ | ✓ | ✓ |
| If session OHLC/volume empty/zero → history bars (outside-RTH rule) | ✓ | ✓ | ✓ |
| Short history (5m and/or 1d bars) | ✓ | ✓ | ✓ |
| X sample with cites (sentiment/path needs) | △ | △ | △ |
| Web: next catalysts / recent news | — | ✓ | ✓ |
| Web: key financials / margins / FCF snippets | — | ✓ if thesis | ✓ |
| Web: Form 4 / 13F if ownership matters | — | △ | ✓ forensic/value |
| Risk factors / footnote anomalies scan | — | △ | ✓ forensic |
| IBKR themes/connections if chain/peer thesis | — | △ | ✓ |
| Options surface if §5/§13 options path | △ | △ | △ |
| Bias 5-scan if deep / etf sleeve / serenity (§C.2b) | △ | ✓ | ✓ |

△ = when path requires it. **Do not invent** missing rows — DATA_GAP.

### Step 1 · Problem review + Review the Givens

1. Restate real question; flag unverified user assumptions.  
2. Classify path.  
3. **Givens table** → write `SESSION_CACHE.givens` (lite ≥1 row; standard/max full):

| Given / assumption | Status: valid / weakened / invalid | Impact on leading view |
|--------------------|------------------------------------|------------------------|

If leading view dies without weakened givens → revise **before** concluding.

### Step 1b · Timeline overlay (when causal) · Suite1 R4

**When:** earnings reactions, “why moved”, capital raises, multi-event weeks, max forensic.  
**Else:** one line `Timeline: N/A`.

Build a **dated spine** (event → lag → print/tape). Mark impossible sequences. Do not assert cause without sequence feasibility. Prefer IBKR timestamps + Web dated headlines.

### Step 2 · Hypothesis expansion + multi-cause + asymmetry

1. Hypotheses: **lite** ≥2 if directional; **standard/max** ≥3 on non-trivial, including ≥1 counter-narrative when a dominant story exists.  
2. **Multiple-cause decomposition** (mandatory **max**; standard on multi-driver moves; lite optional): parallel streams (“&”).  
3. **Asymmetry scan:** breaks vs history, peers, disclosure, capital vs strategy (**standard/max**).  
4. Optional **reverse reconstruction** from low-signal L0 (**max** / forensic).  
5. Persist survivors to `SESSION_CACHE.active_hypotheses`.

### Step 3 · Active falsification + physical priority

1. Hunt **disconfirming** evidence first.  
2. **Physical/mechanical weight:** FCF, inventory/DSO (filings), IBKR volume/liquidity, Form 4, IBKR IV/OI — over guidance/X hype.  
3. Stress-test weakest assumption (**standard/max**).  
4. May **§H INVOKE** L2 only if **§0.5.4 allowlist** + budget.  
5. A3: deterioration → elevate risk, do not protect thesis.

### Step 4 · Convergence + Occam + Bayes-style update + conf v3.0

1. Surviving hypotheses only.  
2. **Occam under uncertainty:** rank by explanatory power vs contortion cost; prefer simpler mechanism unless hard-to-fake L0 forces a heavier model. Elegance ≠ evidence.  
3. **Bayesian-style re-rank (no fake %):** after each material new L0, one line: `Update: H1↑/H2↓ because <L0 id>`. Never invent “73.2% probability”.  
4. Run **§1.4 Confidence** → **CONFIDENCE_BLOCK**; store `last_confidence_block`.  
5. Map uncertainties + kill data.

### Step 5 · Path exposure + Challenge Nodes + error correction

1. Show L0–L3 (see §1.3).  
2. Emit **CHALLENGE_NODES** (§1.5) — counts by mode.  
3. On new contradicting evidence:

```text
Previous inference at Layer <L#> is invalidated by new data <Y>. Re-deriving from this point.
```

4. Append `{layer, old_claim, new_l0}` to `invalidation_stack`; re-run from invalidated step; refresh hypotheses + conf.

### §1.3 Inference layers

| Layer | Meaning |
|-------|---------|
| **L0** | Raw sourced observation |
| **L1** | Direct implication; most observers would agree |
| **L2** | Needs extra assumption(s) — list them |
| **L3** | Unconfirmed hypothesis — list kill/elevate conditions |

Never present L2/L3 as L0/L1.

> **§1.4 and §1.5 live in `SKILL.md`.** Do not fork dims or CN schema.

---

## §M Method Library (Cog-3 · on-demand only)

**Canonical index:** `method-library/INDEX.md`  
**First-12 cards:** M01–M12 under `references/method-library/{think,judge,speak,limits}/`.

### M.1 Non-negotiable load rules

1. **Never** load the entire `method-library/` tree into context.  
2. **Never** load cards in **lite** (`method_cards_loaded=[]`, `method_cards_skipped=lite`).  
3. **standard:** load at most **3** cards whose triggers match.  
4. **max:** load at most **6** cards (even if more match); rank per INDEX.  
5. If tool budget nearly spent → skip cards; `method_cards_skipped=budget`.  
6. Cards **augment** §1 Steps 2–5; they do **not** replace §D, §9, §H, or conf v3.0.  
7. After selection, record `METHOD_CARDS_LOADED: [M05, M01, …]` in working notes and SESSION_CACHE.  
8. User may force: `use method M05` / `load physical priority card` → load that id if mode ≠ lite (lite: ignore or upgrade note).

### M.2 Quick trigger map (see INDEX for full)

| Intent / path | Prefer cards |
|---------------|--------------|
| Premature thesis / headline reaction | M01, M04 |
| Forensic / fragmented / footnotes | M02, M07, M05 |
| Peer/pattern break | M03 |
| Quality of earnings / undervalued | M05, M10, M09 |
| Fraud / collusion talk | M06, M05 |
| Management strategy credibility | M09, M08, M10 |
| Long max write-up | M11 |
| Story stock / euphoria | M12, M05 |

### M.3 Invocation template

```text
# After Step 0, before Step 2 (or when forensic branch starts):
READ references/method-library/INDEX.md          # selection only — do not ingest all card bodies
LOAD references/method-library/<subdir>/<file>.md  # only chosen ids, ≤ mode max
```

Paths must exist under `sherlock/references/method-library/`. No other directories.

---

## §2 Domain analysis methods (governed by §1)

### L1 Denoise
Structural vs emotional vs technical noise. Strip emotion: does price logic hold?

### L2 Cui Bono
Who benefits? Capability? Pre-move positioning/behavior?

### L3 Narrative interrogation
Dominant story = primary suspect. Find cracks (price vs story, insiders reverse).

### L4 Counterfactual
If wrong, which **observable** metric in which window appears?

### L5 Confidence
**Delegated to §1.4** (v3.0). Do not use pre-v3.0 “three bullet” A/B/C alone on FULL paths.

---

## §3 Anti-disguise (US corporate)

1. Smoke-screen: crisis/PR vs accumulation  
2. Loading-dock: narrative vs physical/ops metrics (Web + IBKR activity)  
3. Agent motives: comp vs strategy; **role-behavior consistency**  
4. Capital maze: related party, opacity → risk discount  
5. Liability capitalization: litigation/regulatory as contingent liability  

Feed asymmetries from §1 Step 2 into this section when relevant.

---

## §4 Non-US markets

**Disabled.** No HK/A-share LHB/游资 pipelines. State US-only and stop.

---

## §5 US equities ops protocols

### Name buckets
A large/covered · B mid growth · C SPAC/IPO caution · D <$5 avoid

### Options signals → IBKR only

| Signal | Prefer |
|--------|--------|
| Near-term call volume | chain + snapshot volume/OI |
| IV rise without price move | `implied_vol_underlying` / percentile |
| Call/put skew | underlying option volume fields |
| OTM call cluster | bounded chain + snapshots |
| OI jump | OI compare or Web DATA_GAP |

Signal → Cui Bono; no auto entry.

### Short squeeze (4 layers)
SI>15% + DTC>3 (Web) · catalyst · not under brick wall · tape+options confirm. Need ≥3 layers.

### Earnings trade
Independent edge required; momentum-only ≤ B; no hold-through-print as default research advice.

### Book discipline (research framing)
A-grade ideas preferred; C-grade narrative ≤30% book story; avoid >50% same macro factor.

### Capital envelope
- Do not invent a monthly cash ceiling. The historical ~USD 1000 line does not apply to existing IBKR or Schwab positions.  
- Read the live book from `../../../contracts/data-pack.md`.  
- Size a new buy only after the skill entry's advice card, and only if the user states a cash figure.  
- Detail: `../../modules/etf/references/user-capital-policy.md`. Grouping: `../../../contracts/book-and-overlaps.md`.

---

## §6 Domain veto (buy narrative)

Any hit → **stop buy narrative**, report reason. Runs under §C.

0. **trap-detector** first (tip keywords) → 🟠/🔴 hard stop  
1. Macro: VIX>30 rising · Fed high-uncertainty week · DXY ~10d >3%  
2. Name: Cui Bono empty when required · liquidity fail · counterfactuals blank  
3. Cognitive: revenge trading · zombie interest · one-sided emotion  

Data via §D only.

---

## §7 Cross-asset (US lens)

Rates · USD · oil · VIX · BTC-as-risk-proxy. **Divergence > convergence** as investigation priority.

---

### §8.1 FULL / standard / max template

```markdown
## [Ticker / question]
**mode_effective:** lite|standard|max

### L0 Observations
- … (source: IBKR|WEB|X)

### Review the Givens
| Given | Status | Impact |

### Timeline (or N/A)
…

### Hypotheses (multi-cause)
| ID | Streams (&) | Status | Kill | Occam rank |

### Update log (Bayes-style, if new L0)
- …

### L1–L3 Inference
…

### Falsification notes
…

### Cui Bono / Asymmetry
…

### Silent dogs
…

### CONFIDENCE_BLOCK
…

### CHALLENGE_NODES
…

### Conclusion
Provisional view + assumptions + risks + next data (not a broker order)
```

---

### 9.1 Tree

> **Bot routines do not start this tree.** They follow the skill entry's runbooks: KOL posts → data pack → engine analysis → advice card. This tree applies when the user names desk-style research.

```
User request
├── 🔴 trap keywords → trap-detector → STOP if elevated  [all modes]
├── ⏱ intraday (1–7d tape) → §12  [preferred in lite]
├── 📅 short path 1–4w → §13  [lite=short; standard/max=full calendar]
├── 🚀 Serenity / high-beta / screen
│     lite: ✗ block multi-deep DAG (offer upgrade to max)
│     standard: ① x-adv → ② serenity? → ③ deep×≤1
│     max: ①→②→③ deep×≤3 + DATA_PACK.DEEP
│     conf: pre-deep names ≤B
├── 🔍 named deep / buy?
│     lite: auto-upgrade to standard if deep keywords; else refuse full deep
│     standard/max: deep-analysis + §1 + §5 + §6; buy → §10
│     panel: standard/max only
├── 📐 single-dim → tools if allowlist (lite: only if explicit)
├── 📦 ETF plan / product / sleeves / opportunity window
│     → etf  [standard/max; lite only if user explicit]
│     → etf-premium optional for NAV premium entry check
│     inverse ETFs: taxonomy only / no investment path
│     levered long: tactical short-horizon only (not core)
├── 📡 quote/K → §D; sentiment → finance-sentiment and/or x-adv  [all modes]
├── 🔬 forensic → standard/max (§3 + fundamentals)
├── 🌍 macro → §2 + §7
└── pure narrative → §2 L3/L4 + conf
```

### 9.2 Active L2 (route only these)

```
engine module x-advanced-research: 
engine module serenity: 
engine module etf:                           # top-level ETF plan M1–M7
engine modules UZI: deep-analysis|investor-panel|trap-detector
engine modules finance-skills: 
  company-valuation|earnings-recap|earnings-preview|estimate-analysis|
  sepa-strategy|options-payoff|stock-liquidity|stock-correlation|
  finance-sentiment|etf-premium|saas-valuation-compression|
  startup-analysis|hormuz-strait
```

**Never route:** banned skills (yfinance, funda, readers, lhb, China panel groups) — see `banned-patterns.yaml`.

### 9.3 Conflicts
Deep+intraday → §12 first (then offer standard deep).  
`mode_profile` vs deep keywords → `mode_effective` (§0.5.3).  
Brain §D wins over L2 data text. §C/§1 conf wins over L2 tone.  
Mode allowlist wins over “nice to have” tool sprawl.  
X heat vs X discovery: **sentiment 赢家 = `finance-sentiment`**；找票/movers = `x-advanced-research`。二者同一 X 面 → 不要并行（§H.1）。

> **§9.0 / §9.4 live in `SKILL.md`.** Do not rewrite this §9.1 tree.

---

## §H Handoff (Brain ↔ L2)

### H.1 Rules
≤2 parallel L2 if independent · no L2→L2 · no re-fetch packed keys · **skill must be allowlisted for mode_effective** · Brain merges SESSION_CACHE.

### H.2 INVOKE

```text
### INVOKE
skill: <engine module>/GUIDE.md
intent: ...
ticker: SYM
contract_id: ...
budget: { max_new_tool_calls, may_fetch }
data_pack: |
  ...
return_schema: RETURN_BLOCK
```

### H.3 RETURN_BLOCK

```text
### RETURN_BLOCK
skill: ...
status: ok|partial|blocked
ticker: ...
confidence: A|B|C
confidence_scope: skill_local|safety|discovery|valuation|panel|sentiment|single_dim
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: [...]
fields_filled: [...]
fields_gap: [...]
artifacts: {...}
counterfactuals: [...]
raw_notes: ≤400 words
```

`confidence` / `confidence_*` = **L2 advisory only** (Cog-4). Full contract: `l2-confidence-contract.md`.  
L2 **must not** emit `### CONFIDENCE_BLOCK` or `mode:`.

### H.4 Validation + **confidence post-conditions** (all modes)

**Structure**
- [ ] RETURN present; ticker match  
- [ ] L2 was allowlisted for `mode_effective`  
- [ ] fields_gap or `data_gaps_material: true` → treat L2 conf as ≤ B input  
- [ ] no lateral skill orders from L2  
- [ ] buy path → §6 then §10  

**Confidence post-conditions (universal · never skip)**
- [ ] Thesis / forecast / buy / screen ranking includes **CONFIDENCE_BLOCK** with `mode:`  
- [ ] Apply **§1.4 mode ceilings**  
- [ ] grade A ⇒ ≥3 independent_chains + assumption_audit=strong  
- [ ] Only X+narrative → ≤ C (A1)  
- [ ] Core DATA_GAP → ≤ B or C  
- [ ] **§H.6 re-grade** after every L2 RETURN (never copy L2 A → user A blindly)  
- [ ] Discovery pre-deep ≤ B  
- [ ] `mode` matches `mode_effective`  
- [ ] Log `L2_CONF_ADVISORY` + `BRAIN_REGRADE` when L2 was used  

**Challenge Nodes post-conditions (Cog-2)**
- [ ] **CHALLENGE_NODES** present with counts per §1.5  
- [ ] Each node has `what_would_falsify` observable  
- [ ] `last_challenge_nodes` written to SESSION_CACHE  

**Method Library post-conditions (Cog-3)**
- [ ] lite → no card bodies loaded  
- [ ] standard ≤3 cards; max ≤6; ids only from INDEX M01–M12  
- [ ] `method_cards_loaded` / `skipped` recorded  
- [ ] Cards did not introduce banned data tools  

### H.5 Discovery chain (mode-gated)

```
lite:     DAG blocked (upgrade message) unless user forces max/standard + accept
standard: ① x-adv → ② serenity? → ③ deep×≤1
max:      ① x-adv → ② serenity → ③ deep×≤3 + DATA_PACK.DEEP
then:     Brain §1 + conf merge → user table
```

No L2 skip-ahead on that chain. Bot routines do not start this DAG. They use the skill entry's runbooks and accounts contract, then valuation and trap. `serenity` and `deep-analysis` run only when the user names them.

> **§H.6 re-grade lives in `GUIDE.md`.**

---

## §10 Direct judgment (“buy/sell now?”)

Only after §6 pass (and §C not blocking):

1. Veto result — a pass may become the advice card defined by the skill entry. A pass is not an order. Orange or red trap does not pass.  
2. Price regime vs this turn's IBKR last and 52w, not a cache file  
3. Capital safety (clear yes/conditional/no)  
4. Catalyst logic (≤3 variables)  
5. Counterfactuals 3–4 with windows  
6. Position **framework** only: `max $ loss ÷ stop%`  
7. **CONFIDENCE_BLOCK** + **CHALLENGE_NODES** required  
8. Ban: vague risk shrug; evidence-free “I like it”; button-push orders  

---

## §13 Swing 1–4 weeks (and 1–3m under **standard**)

Data: §D SWING; **standard/max** add Web catalysts/filings.  
Structure vs MA20/50/200, RSI, volume.  
Catalyst calendar (Web). Optional IBKR options surface.  
Scenario matrix tech × catalyst.  
Output: range + **CONFIDENCE_BLOCK** + **CHALLENGE_NODES** + kills.  
No fake precision points.

---

*full-engine.md · not a skill · READ iff mode_effective ≥ standard · slim A–E*
