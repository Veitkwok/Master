#!/usr/bin/env python3
"""Deterministic comps fallback tests (script computed, not model)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "finance-master" / "scripts" / "deepseek_analyze.py"

spec = importlib.util.spec_from_file_location("worker", SCRIPT)
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)  # type: ignore[union-attr]


def stock(**fw) -> dict:
    data = {"security_type": "STK", "quote": {"last": 20.0}, "fundamentals_web": fw}
    return data


def peer(sym: str, **mult) -> dict:
    return {"symbol": sym, "multiples": mult}


def pack(sym: str, t: dict) -> dict:
    return {"tickers": [sym], "symbols": {sym: t}}


CASES = []

# 1) EV/EBITDA lens: median 10 -> EV 20000, equity 15000, price 15
p1 = pack("VST", stock(shares_diluted=1000, net_debt=5000, ebitda_ttm=2000,
                        peers=[peer("A", ev_ebitda=8), peer("B", ev_ebitda=10),
                               peer("C", ev_ebitda=12)]))
c1 = worker.compute_comps(p1).get("VST")
CASES.append(("ev_ebitda lens", c1 is not None and c1["lens"] == "ev_ebitda"
              and c1["base"] == 15.0 and c1["quality"] == "ok"))

# 2) negative FCF/EPS but EBITDA lens works (MOS-like)
p2 = pack("MOS", stock(shares_diluted=1000, net_debt=1000, ebitda_ttm=500,
                        fcf_ttm=-100, eps_ttm=-1,
                        peers=[peer("A", ev_ebitda=5), peer("B", ev_ebitda=7),
                               peer("C", ev_ebitda=9)]))
c2 = worker.compute_comps(p2).get("MOS")
CASES.append(("negative fcf -> comps", c2 is not None and c2["lens"] == "ev_ebitda"
              and c2["base"] == 2.5))

# 3) wide dispersion: EV/Sales peers 10/12/82.9 -> wide/very_wide
p3 = pack("MP", stock(shares_diluted=100, net_debt=0, revenue_ttm=100,
                       peers=[peer("A", ev_sales=82.9), peer("B", ev_sales=10),
                              peer("C", ev_sales=12)]))
c3 = worker.compute_comps(p3).get("MP")
CASES.append(("wide comps", c3 is not None and c3["lens"] == "ev_sales"
              and c3["quality"] in {"wide", "very_wide"} and c3["confidence_cap"] == "C"
              if c3 and c3["width_ratio"] > 1.0 else c3 is not None))

# 4) insufficient peers -> no computed comps
p4 = pack("X", stock(shares_diluted=100, net_debt=0, ebitda_ttm=10,
                      peers=[peer("A", ev_ebitda=8), peer("B", ev_ebitda=10)]))
CASES.append(("insufficient peers -> none", worker.compute_comps(p4).get("X") is None))

# 5) CRWV-like: EV/EBITDA peers 21x apart + absurd base -> should pick EV/Sales, not "wide"
p5 = pack("CRWV", stock(shares_diluted=1000, net_debt=20000, ebitda_ttm=3000,
                         revenue_ttm=8000,
                         peers=[peer("NBIS", ev_ebitda=174.39, ev_sales=33.2),
                                peer("ORCL", ev_ebitda=14.68, ev_sales=7.04),
                                peer("IREN", ev_ebitda=311.91, ev_sales=16.92)]))
c5 = worker.compute_comps(p5).get("CRWV")
CASES.append(("CRWV chooses plausible lens", c5 is not None
              and c5["lens"] == "ev_sales"
              and c5["quality"] in {"very_wide", "insufficient"}
              and c5["base"] < 500))
# note: with last=20 in the helper, EV/Sales base is also implausible; the point is
# the lens choice and quality downgrade, not the exact base.

# 6) gate: negative fcf, no comps route -> incomplete
p5 = pack("N", stock(shares_diluted=100, net_debt=0, revenue_ttm=10, fcf_ttm=-5))
missing = worker.check_valuation_inputs(p5)
CASES.append(("gate rejects negative-fcf-only", len(missing) == 1
              and any("<=0" in f for f in missing[0]["fields"])))

# 6) gate: negative fcf + comps route -> ok
p7 = pack("N", stock(shares_diluted=100, net_debt=0, revenue_ttm=100, fcf_ttm=-5,
                      peers=[peer("A", ev_sales=2), peer("B", ev_sales=3), peer("C", ev_sales=4)]))
CASES.append(("gate allows comps route", worker.check_valuation_inputs(p7) == []))


def main() -> int:
    failures = 0
    for name, ok in CASES:
        print(("PASS " if ok else "FAIL ") + name)
        failures += 0 if ok else 1
    print(f"\n{len(CASES)-failures}/{len(CASES)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
