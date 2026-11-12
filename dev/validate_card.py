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
HELD_CONTEXTS = {"ibkr", "schwab", "both", "hsbc", "manual", "multi"}
EARN_PHASES = {"preview", "recap"}
EARN_LABELS = {"beat", "inline", "miss"}
GUIDE_DIRS = {"raised", "maintained", "lowered", "none"}


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
    if pos.get("context") not in HELD_CONTEXTS | {"neither", "unknown"}:
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
        if not c.get("position", {}).get("context") in HELD_CONTEXTS:
            e.append("TRIM/SELL requires a held position")

    if stance == "AVOID" and trap not in {"orange", "red"} and not risk.get("avoid_reason"):
        e.append("AVOID needs trap orange/red or risk.avoid_reason")

    if not (c.get("target") or {}).get("basis") and stance in {"BUY", "ADD"}:
        e.append("BUY/ADD requires target.basis")

    if "earnings" in c and c["earnings"] is not None:
        e.extend(validate_earnings(c["earnings"]))
    return e


def validate_earnings(er) -> list[str]:
    """Optional card.earnings block (holdings earnings window, v1.0.31).

    Evidence only: it never changes stance gates. Checks shape, sourcing,
    and that labels/flags agree with the numbers on the card.
    """
    e: list[str] = []
    if not isinstance(er, dict):
        return ["earnings must be an object"]
    phase = er.get("phase")
    if phase not in EARN_PHASES:
        e.append(f"earnings.phase invalid: {phase}")
        return e
    if not er.get("report_date"):
        e.append("earnings.report_date required")
    if not er.get("source_url"):
        e.append("earnings.source_url required (numbers must be sourced)")
    if er.get("timing") not in (None, "BMO", "AMC", "unknown"):
        e.append(f"earnings.timing invalid: {er.get('timing')}")
    if phase == "preview":
        for k in ("eps", "revenue", "guidance_direction", "exit_flags"):
            if er.get(k) not in (None, {}, []):
                e.append(f"earnings.{k} not allowed on preview (no print yet)")
        return e
    labels = {}
    for k in ("eps", "revenue"):
        m = er.get(k)
        if m is None:
            continue
        if not isinstance(m, dict):
            e.append(f"earnings.{k} must be an object")
            continue
        a, b, lab = m.get("actual"), m.get("estimate"), m.get("label")
        if lab not in EARN_LABELS:
            e.append(f"earnings.{k}.label invalid: {lab}")
            continue
        if _num(a) and _num(b):
            # tolerance-aware labels: beat/miss beyond tolerance, inline within it;
            # a technical_miss means actual<estimate but inside tolerance.
            tm = m.get("technical_miss")
            if tm is not None and not isinstance(tm, bool):
                e.append(f"earnings.{k}.technical_miss must be boolean")
            elif lab == "beat" and a < b:
                e.append(f"earnings.{k}.label beat but actual < estimate")
            elif lab == "miss" and a > b:
                e.append(f"earnings.{k}.label miss but actual > estimate")
            elif lab == "inline" and not (a >= b or tm is True):
                e.append(f"earnings.{k}.label inline but actual < estimate (technical_miss missing)")
        else:
            e.append(f"earnings.{k} needs numeric actual and estimate")
        labels[k] = lab
    gd = er.get("guidance_direction")
    if gd is not None and gd not in GUIDE_DIRS:
        e.append(f"earnings.guidance_direction invalid: {gd}")
    flags = er.get("exit_flags") or {}
    if not isinstance(flags, dict):
        return e + ["earnings.exit_flags must be an object"]
    pairs = (("eps_miss", labels.get("eps") == "miss" if "eps" in labels else None),
             ("revenue_miss", labels.get("revenue") == "miss" if "revenue" in labels else None),
             ("guide_lowered", gd == "lowered" if gd is not None else None))
    for key, want in pairs:
        got = flags.get(key)
        if want is not None and got is not want:
            e.append(f"earnings.exit_flags.{key} must be {want}")
    if er.get("override_exit_hit") is True and not er.get("override_note"):
        e.append("earnings.override_exit_hit requires override_note (state it plainly)")
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
