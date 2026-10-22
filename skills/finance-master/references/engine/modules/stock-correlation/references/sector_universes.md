# Dynamic Peer Universe Construction

> ⚠️ **v4.6.8 data fence:** Do **not** `import yfinance`, `pip install yfinance`, or call `yf.*`.  
> Live path: Brain **DATA_PACK** → **IBKR** (`IBKR 主题` / `IBKR 关联`) → **Web**.  
> Algorithms below take **already-fetched** pack / Web fields only.

How to build a peer universe at runtime for correlation analysis. **Do not hardcode ticker lists** when IBKR themes or Web comps are available.

---

## Method 1: IBKR themes / connections (Primary)

```text
INPUTS (from DATA_PACK or IBKR):
  ticker, contract_id
  peers.symbols[]          # from IBKR 主题 / IBKR 关联
  peers.theme_labels[]

ALGORITHM:
  1. Prefer pack.peers.symbols if non-empty
  2. Else Brain/L2 may_fetch → IBKR themes (max_companies per theme) → US STK only
  3. Drop non-US, leveraged single-name ETFs, exact self-ticker
  4. Cap universe size (e.g. 15–30) before correlation
```

Pseudocode (no yfinance):

```python
def get_sector_peers_from_pack(data_pack, max_results=30):
    """Peers from Brain DATA_PACK / IBKR themes only."""
    peers = list(data_pack.get("peers", {}).get("symbols") or [])
    self_sym = data_pack.get("ticker")
    out = [s for s in peers if s and s != self_sym][:max_results]
    return out
```

If pack peers empty and `budget.may_fetch`: resolve themes via IBKR MCP tools — **not** Yahoo screener APIs.

---

## Method 2: Thematic expansion (Web + IBKR)

```text
INPUTS:
  pack.fundamentals_web / Web business description
  pack.peers.theme_labels
  optional Web industry peers

ALGORITHM:
  1. Read sector / industry / product graph from pack or IBKR connections
  2. Add 1–2 adjacent themes (e.g. semi equipment next to GPU names)
  3. Union with Method 1; dedupe; US-list only
```

```python
def get_thematic_context_from_pack(data_pack):
    return {
        "sector": data_pack.get("sector") or data_pack.get("fundamentals_web", {}).get("sector", ""),
        "industry": data_pack.get("industry") or "",
        "description": data_pack.get("profile_note") or "",
        "themes": data_pack.get("peers", {}).get("theme_labels") or [],
    }
```

Examples of adjacent themes (logic only):

- Semiconductor → equipment / materials  
- Cloud platform → networking / data-center power  
- EV maker → battery materials / auto parts  

---

## Combining methods

```python
def build_peer_universe(data_pack):
    peers = set(get_sector_peers_from_pack(data_pack, max_results=25))
    ctx = get_thematic_context_from_pack(data_pack)
    # optional: merge Web comps table tickers already in pack
    for s in data_pack.get("comps_tickers") or []:
        if s and s != data_pack.get("ticker"):
            peers.add(s)
    return sorted(peers)
```

If `len(peers) < 5`: mark `DATA_GAP: peers` and lower conf (≤ B) rather than inventing a universe.

---

## Correlation math (unchanged intent)

Once you have peer symbols + IBKR/Web price history for each:

1. Align daily closes  
2. Compute returns correlation matrix  
3. Report top-N correlated peers + note sample window  

**Price history source:** IBKR `IBKR 历史K线` or pack `ohlcv.daily` — never yfinance downloads.

---

*v4.6.8 · IBKR/Web peers only · yfinance fenced*
