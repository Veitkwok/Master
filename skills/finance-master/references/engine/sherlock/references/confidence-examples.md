# Confidence v3.0 · Worked examples (IBKR / Web / X)

Load on demand when calibrating grades. **Independent chains** must be distinct classes: IBKR market · primary filing/transcript · ownership · **ETF issuer primary** · (at most one) X cluster.  
**Not a chain:** a research-cache digest (this pack has none), social heat, invented valuation bands.

---

## Example A — grade A (standard/max)

```text
### CONFIDENCE_BLOCK
grade: A
mode: standard
dims:
  evidence_independence: strong
  falsification_rigor: strong
  assumption_audit: strong
  physical_mechanical: strong
  layer_integrity: strong
limiting: []
verification_density: "Three independent chains (IBKR tape+ADV, 10-Q FCF conversion, Form 4 cluster) survive explicit margin-compression and guidance-miss attacks; Givens re-audited this turn."
independent_chains:
  - "IBKR: last/volume/ADV + 52w position"
  - "WEB: 10-Q cash from ops vs net income"
  - "WEB: Form 4 net buying last 90d"
```

**Illegal A:** three news URLs retelling the same earnings headline.

---

## Example B — grade B (lite short-term)

```text
### CONFIDENCE_BLOCK
grade: B
mode: lite
dims:
  evidence_independence: weak
  falsification_rigor: weak
  assumption_audit: strong
  physical_mechanical: strong
  layer_integrity: strong
limiting: [evidence_independence, falsification_rigor]
verification_density: "IBKR 5m structure supports range thesis; only one secondary Web catalyst note; X heat is single chain and not used for A. Limited falsification on gap-fill scenario."
independent_chains:
  - "IBKR: 5m OHLCV wave structure + volume ratio"
  - "WEB: event calendar date T+2"
```

---

## Example C — grade C (X-heavy / thin)

```text
### CONFIDENCE_BLOCK
grade: C
mode: lite
dims:
  evidence_independence: gap
  falsification_rigor: gap
  assumption_audit: weak
  physical_mechanical: gap
  layer_integrity: strong
limiting: [evidence_independence, falsification_rigor, physical_mechanical]
verification_density: "A1: directional claim rests primarily on X discussion cluster without IBKR confirmation of breakout volume; no filing-level physical check."
independent_chains:
  - "X: high-engagement posts 48h (single social chain)"
```

**Rule:** pure X → **≤C**. Add IBKR breakout volume + one Web primary before considering B.

---

## Skeptic bar (A)

A-grade should be hard for a competent skeptic to dismantle **without new contradictory L0**. If a skeptic can kill the thesis with one obvious unanswered DATA_GAP, grade is not A.

---

## Cog-4 · L2 advisory vs Brain re-grade

L2 emits skill-local `confidence` only. Brain always owns `### CONFIDENCE_BLOCK`. Full rules: `l2-confidence-contract.md`.

### Example — valuation L2 A → Brain B

```text
### RETURN_BLOCK
skill: company-valuation
status: ok
ticker: MSFT
confidence: A
confidence_scope: valuation
confidence_basis:
  evidence_independence: strong
  physical_mechanical: strong
  data_gaps_material: true
limiting_factors: ["full_segment_model gap", "synthetic WACC band"]
fields_gap: [full_segment_model]
...
```

```text
L2_CONF_ADVISORY: A (company-valuation, scope=valuation)
BRAIN_REGRADE: B (reason: material fields_gap + weak falsification; §H.6)

### CONFIDENCE_BLOCK
grade: B
mode: standard
dims:
  evidence_independence: strong
  falsification_rigor: weak
  assumption_audit: strong
  physical_mechanical: strong
  layer_integrity: strong
limiting: [falsification_rigor]
...
```

### Example — discovery L2 A stays pre-deep B

```text
L2_CONF_ADVISORY: A (serenity-skill, scope=discovery)
BRAIN_REGRADE: B (reason: pre-deep shortlist ceiling; deep not complete)
```

### Example — trap safety A (not a buy grade)

```text
L2_CONF_ADVISORY: A (trap-detector, scope=safety)
BRAIN_REGRADE: A (safety classification only; hard_stop; no investment thesis)
```

### Example — ETF sleeve lite B (issuer + optional IBKR; research-research-cache/social excluded)

```text
L2_CONF_ADVISORY: B (etf, scope=single_dim)
BRAIN_REGRADE: B (reason: lite ceiling + <3 chains; research-research-cache/social not A-chains)

### CONFIDENCE_BLOCK
grade: B
mode: lite
dims:
  evidence_independence: weak
  falsification_rigor: weak
  assumption_audit: strong
  physical_mechanical: strong
  layer_integrity: strong
limiting: [lite_ceiling, only_two_independent_chains, scout_heat_excluded, cache_not_a_chain]
verification_density: "Issuer ER/holdings/index dated; IBKR structure if available. Cache one_liner reused only as digest. Scout heat attic-rejected."
independent_chains:
  - "IBKR: quote/spread/ADV/TNA"
  - "WEB: issuer ER + Nasdaq-100 holdings asof"
```

If `ibkr_available=false`, drop the IBKR line, set physical **weak**, keep grade **B** (or C if issuer also missing).

**Illegal A:** counting a cached quote file as a third independent chain.

### Example — etf L2 A with overlap gap → Brain B

```text
L2_CONF_ADVISORY: A (etf, scope=single_dim)
BRAIN_REGRADE: B (reason: fields_gap overlap_quant + “diversifier” claim unverified)

### CONFIDENCE_BLOCK
grade: B
mode: standard
dims:
  evidence_independence: strong
  falsification_rigor: weak
  assumption_audit: strong
  physical_mechanical: strong
  layer_integrity: strong
limiting: [no_M3_overlap_quant]
```

### Illegal

- Copying L2 `confidence: A` into user conclusion without CONFIDENCE_BLOCK  
- Emitting CONFIDENCE_BLOCK from L2 skill body  
- Treating panel voter 0–100 scores as Brain grade A
- Treating research-cache digest or Scout heat as an A-chain
