#!/usr/bin/env python3
"""Golden / negative advice-card tests for the Master pack.

    python3 dev/tests/test_cards.py

Covers the money-safety rules: trap gate, missing target, missing invalidation,
confidence gate, order flags, chained sell.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_card import validate  # noqa: E402


BASE = {
    "card_version": 1,
    "asof": "2026-10-23T07:34:00+08:00",
    "routine": "primary_babybus",
    "symbol": "NVDA",
    "stance": "BUY",
    "last": 182.40,
    "entry_limit": 186.00,
    "target": {"base": 224.00, "low": 205.00, "high": 243.00,
               "basis": "dcf_blend", "horizon": "6-12m"},
    "upside_pct": 22.8,
    "sell_plan": {"invalidation_price": 158.00,
                  "invalidation_thesis": "下季指引下调",
                  "review_by": "2027-02-20"},
    "position": {"context": "ibkr", "qty": 12, "avg_cost": 171.20,
                 "market_value": 2188.80, "unrealized_pct": 6.5},
    "risk": {"trap_level": "green", "priced_in": "partial", "confidence": "B",
             "limiting": [], "chains": "IBKR+WEB", "key_risks": [], "overlap": []},
    "data_gaps": [],
    "analysis_source": "deepseek",
    "order_sent": False,
    "schwab_trade": "forbidden",
    "draft_created": False,
}


def case(name, expected_ok, **overrides):
    card = dict(BASE)
    for k, v in overrides.items():
        if isinstance(v, dict) and isinstance(card.get(k), dict):
            merged = dict(card[k])
            merged.update(v)
            card[k] = merged
        else:
            card[k] = v
    errors = validate(card)
    ok = not errors
    return name, expected_ok, ok, errors


CASES = [
    case("gold: new buy with all gates", True),
    case("gold: held trim at target", True, stance="TRIM",
         last=226.0, entry_limit=None, position={"context": "ibkr"}),
    case("gold: watch when target missing", True, stance="WATCH",
         target={"base": None}, upside_pct=None, entry_limit=None),
    case("neg: trap orange cannot buy", False, risk={"trap_level": "orange"}),
    case("neg: confidence C cannot buy", False, risk={"confidence": "C"}),
    case("neg: priced_in priced cannot buy", False, risk={"priced_in": "priced"}),
    case("neg: missing target cannot buy", False, target={"base": None},
         upside_pct=None),
    case("neg: missing invalidation cannot buy", False,
         sell_plan={"invalidation_price": None, "invalidation_thesis": ""}),
    case("neg: order_sent true is illegal", False, order_sent=True),
    case("neg: schwab_trade allowed is illegal", False, schwab_trade="allowed"),
    case("neg: chase above entry limit", False, last=190.0),
    case("neg: upside below 20%", False, target={"base": 210.0}, upside_pct=15.2),
]


def main() -> int:
    failures = 0
    for name, expected_ok, ok, errors in CASES:
        status = "PASS" if ok == expected_ok else "FAIL"
        if status == "FAIL":
            failures += 1
            print(f"{status} {name}")
            for err in errors:
                print("   -", err)
        else:
            print(f"{status} {name}")
    print(f"\n{len(CASES) - failures}/{len(CASES)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
