---
name: finance-sentiment
description: >
  US ticker social/news sentiment via native X tools + Web (optional Reddit via Web).
  v4.6.8 Grok-native — no Adanos API key required, no Hermes readers.
  Triggers: sentiment, buzz, what is X saying, social heat, bullish percentage, narrative.
version: 4.6.8
ecosystem: 4.6.8
metadata:
  tags: [finance, us-stocks, sentiment, x-twitter]
  market_scope: US_EQUITIES_ONLY
  role: L2_TOOL
---

# Finance Sentiment · v4.6.8 (X + Web)

## Consumer rules

| Source | How |
|--------|-----|
| X / Twitter | Bot 内置 X 读取器（关键词 / 语义 / 帖子与线程） |
| News tone | Web search headlines |
| Reddit | Web search `site:reddit.com` only if useful (no API key) |
| Polymarket | Web only if user asks |

**Do not** require `ADANOS_API_KEY`, twitter-reader, or other opencli readers.  
If Brain already filled `social_x` in pack → **reuse**. Cap ~6–10 searches.

## Framework

1. Sample recent high-signal posts (min engagement when possible)  
2. Bucket: bullish / bearish / neutral / junk  
3. Themes (3–5 bullets) with cites  
4. Heat: rising / stable / fading (qualitative)  
5. Divergence: price up + social panic (or reverse) if pack quote available  

```text

## L2 confidence (Cog-4 · advisory only)

`confidence` in `### RETURN_BLOCK` is **skill-local deliverable quality**, not user investment confidence.

| Rule | Max grade |
|------|-----------|
| `status: partial` or material `fields_gap` | **B** |
| X/social-only evidence for hard claims | **C** |
| `status: blocked` | no thesis A |
| Complete skill scope + hard sources + no material gaps | **A** allowed (still advisory) |

Default `confidence_scope` for this skill: **sentiment**.

X/social-heavy packs default **≤ C** for directional market claims; grade A only if multi-source hard corroboration is in-pack (rare for pure sentiment).

Also emit Cog-4 fields when practical: `confidence_scope`, `confidence_basis` (evidence_independence, physical_mechanical, data_gaps_material), `limiting_factors`.

**Never** emit Brain `### CONFIDENCE_BLOCK` or `mode:` — the Central Brain re-grades via §H.6.

### RETURN_BLOCK
skill: finance-sentiment
status: ok|partial
ticker: SYM
confidence: A|B|C
confidence_scope: sentiment
confidence_basis:
  evidence_independence: strong|weak|gap
  physical_mechanical: strong|weak|gap
  data_gaps_material: true|false
limiting_factors: []
fields_filled: [x_sample, themes]
fields_gap: [...]
artifacts:
  bias: bullish|bearish|mixed|unclear
  heat: rising|stable|fading
  themes: [...]
  citations: [urls or post refs]
counterfactuals: []
raw_notes: <≤250 words>
```

Legacy `references/api_reference.md` (Adanos) is **optional offline** — not required for v4.6.8.

*v4.6.8 · DATA_PACK consumer · Cog-4 conf advisory · IBKR market-data only*
