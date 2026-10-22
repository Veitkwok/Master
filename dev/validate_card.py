#!/usr/bin/env python3
"""Validate one advice card (JSON) against the Master decision rules.

    python3 dev/validate_card.py card.json

Importable:

    from validate_card import validate
    errors = validate(card_dict)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

STANCES = {"BUY", "ADD", "HOLD", "TRIM", "SELL", "AVOID", "WATCH"}
TRAP = {"green", "yellow", "orange", "red"}
PRICED = {"not_priced", "partial", "priced", "gap"}
SOURCES = {"deepseek", "bot-inline", "mixed"}


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate(c: dict) -> list[str]:
    e: list[str] = []

    def need(key, msg="missing"):
        cur = c
        for part in key.split("."):
            if not isinstance(cur, dict) or part not in cur:
                e.append(f"{msg}: {key}")
                return None
            cur = cur[part]
        return cur

    for k in ("card_version", "asof", "routine", "symbol", "stance",
              "last", "position", "risk", "analysis_source"):
        need(k)
    if c.get("stance") not in STANCES:
        e.append(f"stance invalid: {c.get('stance')}")
    if not _num(c.get("last")) or c.get("last", 0) <= 0:
        e.append("last must be a positive number")
    if c.get("order_sent") is not False:
        e.append("order_sent must be false")
    if c.get("schwab_trade") != "forbidden":
        e.append("schwab_trade must be forbidden")
    if c.get("draft_created") not in (False, None):
        e.append("draft_created must be false")
    if c.get("analysis_source") not in SOURCES:
        e.append(f"analysis_source invalid: {c.get('analysis_source')}")

    pos = c.get("position") or {}
    if pos.get("context") not in {"ibkr", "schwab", "both", "neither", "unknown"}:
        e.append("position.context invalid")

    risk = c.get("risk") or {}
    conf = risk.get("confidence")
    if conf not in {"A", "B", "C"}:
        e.append(f"risk.confidence invalid: {conf}")
    trap = risk.get("trap_level")
    if trap is not None and trap not in TRAP:
        e.append(f"risk.trap_level invalid: {trap}")
    priced = risk.get("priced_in")
    if priced is not None and priced not in PRICED:
        e.append(f"risk.priced_in invalid: {priced}")

    stance = c.get("stance")
    target = (c.get("target") or {}).get("base")
    upside = c.get("upside_pct")
    entry = c.get("entry_limit")
    sp = c.get("sell_plan") or {}

    if stance in {"BUY", "ADD"}:
        if conf not in {"A", "B"}:
            e.append(f"{stance} requires confidence A/B, got {conf}")
        if trap in {"orange", "red"}:
            e.append(f"{stance} forbidden when trap_level={trap}")
        if priced in {"priced", "gap"}:
            e.append(f"{stance} forbidden when priced_in={priced}")
        if not _num(target) or target <= 0:
            e.append(f"{stance} requires target.base")
        if not _num(entry) or entry <= 0:
            e.append(f"{stance} requires entry_limit")
        if sp.get("invalidation_price") in (None, "") and not sp.get("invalidation_thesis"):
            e.append(f"{stance} requires invalidation (price or thesis)")
        min_upside = 0.20 if stance == "BUY" else 0.15
        if _num(target) and _num(c.get("last")):
            calc = (target - c["last"]) / c["last"]
            if calc < min_upside - 1e-9:
                e.append(f"{stance} requires upside >= {min_upside:.0%}, got {calc:.1%}")
        if _num(entry) and _num(c.get("last")) and c["last"] > entry:
            e.append(f"{stance} but last > entry_limit (do not chase)")
        if _num(entry) and _num(target) and entry > target * 0.85 + 1e-6:
            e.append(f"{stance} entry_limit above target.base*0.85")
        if upside is not None and _num(upside) and _num(target) and _num(c.get("last")):
            if abs(upside - (target - c["last"]) / c["last"] * 100) > 0.5:
                e.append("upside_pct inconsistent with last/target")

    if stance in {"TRIM", "SELL"}:
        if not any(x in c for x in ("target", "sell_plan")) and not sp.get("invalidation_price"):
            e.append("TRIM/SELL needs a trigger (target or invalidation)")
        if not c.get("position", {}).get("context") in {"ibkr", "schwab", "both"}:
            e.append("TRIM/SELL requires a held position")

    if stance == "AVOID" and trap not in {"orange", "red"} and not risk.get("avoid_reason"):
        e.append("AVOID needs trap orange/red or risk.avoid_reason")

    if not (c.get("target") or {}).get("basis") and stance in {"BUY", "ADD"}:
        e.append("BUY/ADD requires target.basis")
    return e


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_card.py card.json", file=sys.stderr)
        return 2
    card = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    errors = validate(card)
    for err in errors:
        print("ERROR:", err)
    print(f"validate_card: {len(errors)} error(s)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
