#!/usr/bin/env python3
"""Manual holdings merge (v1.0.32).

    python3 dev/tests/test_holdings_merge.py

Covers: IBKR+Schwab+HSBC merge, weighted average cost, breakdown string,
AVGO as a held manual-only ticker, concentration including HSBC, stale >30d
gap, missing file, live-broker rejection, context values, card validation.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dev"))
from validate_card import validate  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_cards import BASE  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "merge_holdings", ROOT / "skills/finance-master/scripts/merge_holdings.py")
mh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mh)  # type: ignore[union-attr]

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail if not ok else ""))


def book(**kwargs):
    live = kwargs.pop("live", {
        "ibkr": [
            {"symbol": "MOS", "qty": 5, "avg_cost": 19.71526},
            {"symbol": "CRWV", "qty": 18, "avg_cost": 68.62745556},
            {"symbol": "VST", "qty": 3, "avg_cost": 154.18696667},
        ],
        "schwab": [
            {"symbol": "MOS", "shares": 3, "cost_basis": 61.43},
            {"symbol": "CRWV", "shares": 8, "cost_basis": 711.20},
        ],
    })
    manual = kwargs.pop("manual_lots", [
        {"broker": "HSBC", "symbol": "MOS", "shares": 27, "avg_cost": 20.428,
         "as_of": "2026-11-11", "source": "Veit chat 2026-11-11"},
        {"broker": "HSBC", "symbol": "AVGO", "shares": 2, "avg_cost": 360.740,
         "as_of": "2026-11-11", "source": "Veit chat 2026-11-11"},
    ])
    prices = kwargs.pop("prices", {
        "CRWV": {"last": 56.22, "asof": "2026-11-10 23:56 ET / IBKR last"},
        "MOS": {"last": 22.88, "asof": "2026-11-11 10:25 +08 / IBKR last"},
        "VST": {"last": 133.58, "asof": "2026-11-10 23:53 ET / IBKR last"},
        "AVGO": {"last": 341.26, "asof": "2026-11-10 23:56 ET / IBKR last"},
    })
    run_on = kwargs.pop("run_on", date(2026, 11, 11))
    themes = kwargs.pop("themes", {
        "CRWV": "AI capex/power", "VST": "AI capex/power",
        "AVGO": "semiconductor", "MOS": "fertilizer",
    })
    stale_after = kwargs.pop("stale_after", 30)
    live_lots = mh.load_live(live)
    # build manual lots via a temp file so schema validation is exercised
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"schema": mh.SCHEMA, "positions": manual}, f)
        path = Path(f.name)
    try:
        manual_lots, notices = mh.load_manual(path)
    finally:
        path.unlink(missing_ok=True)
    out = mh.merge_book(live_lots, manual_lots, mh.load_prices(prices),
                        run_on, stale_after, themes)
    out["_notices"] = notices
    return out


def by_sym(out):
    return {p["symbol"]: p for p in out["positions"]}


# ---- merge arithmetic -----------------------------------------------------
out = book()
pos = by_sym(out)
mos = pos["MOS"]
avgo = pos["AVGO"]
check("MOS total shares 35", mos["qty"] == 35, str(mos["qty"]))
expected_avg = (Decimal("5") * Decimal("19.71526")
                + Decimal("61.43")
                + Decimal("27") * Decimal("20.428")) / Decimal("35")
check("MOS weighted avg cost exact to 6dp",
      abs(Decimal(str(mos["avg_cost"])) - expected_avg.quantize(Decimal("0.000001"))) < Decimal("0.000001"),
      f"{mos['avg_cost']} vs {expected_avg}")
check("MOS breakdown string",
      mos["breakdown"] == "MOS 35（IBKR 5+Schwab 3+HSBC 27）",
      mos["breakdown"])
check("MOS context is multi (IBKR+Schwab+HSBC)", mos["context"] == "multi", mos["context"])
check("MOS market value 35 * 22.88", mos["market_value"] == 800.80, str(mos["market_value"]))
check("MOS note flags HSBC as manual with as_of",
      mos["manual_note"] == "HSBC 数量为手工录入（as_of 2026-11-11，有过期风险）",
      str(mos["manual_note"]))
check("AVGO is present as a held ticker", "AVGO" in pos, str(list(pos)))
check("AVGO 2 shares, context hsbc",
      avgo["qty"] == 2 and avgo["context"] == "hsbc",
      f"qty={avgo['qty']} ctx={avgo['context']}")
check("AVGO avg_cost 360.740 preserved",
      abs(avgo["avg_cost"] - 360.74) < 1e-9, str(avgo["avg_cost"]))
check("AVGO market value 2 * 341.26", avgo["market_value"] == 682.52, str(avgo["market_value"]))
check("AVGO breakdown", avgo["breakdown"] == "AVGO 2（HSBC 2）", avgo["breakdown"])
check("as_of 2026-11-11 is not stale on run 2026-11-11",
      out["gaps"] == [], str(out["gaps"]))

# concentration
total = Decimal("26") * Decimal("56.22") + Decimal("3") * Decimal("133.58") \
    + Decimal("35") * Decimal("22.88") + Decimal("2") * Decimal("341.26")
check("portfolio MV includes HSBC MOS+AVGO",
      abs(Decimal(str(out["totals"]["market_value"])) - total.quantize(Decimal("0.01"))) < Decimal("0.01"),
      f"{out['totals']['market_value']} vs {total}")
check("top2 by value is CRWV+MOS",
      out["totals"]["top2_by_value"]["symbols"] == ["CRWV", "MOS"],
      str(out["totals"]["top2_by_value"]))
crwv_mos = (Decimal("26") * Decimal("56.22") + Decimal("35") * Decimal("22.88")) / total * 100
check("top2 by value pct ~67.6",
      abs(out["totals"]["top2_by_value"]["pct"] - float(crwv_mos.quantize(Decimal("0.1")))) < 0.05,
      str(out["totals"]["top2_by_value"]["pct"]))
theme = out["totals"]["theme"]["top2_same_theme"]
check("top2 same theme remains CRWV+VST",
      theme and theme["symbols"] == ["CRWV", "VST"], str(theme))
# HSBC inclusion must pull the old 90% figure down
check("same-theme concentration well below 90 after HSBC",
      theme["pct"] < 80, str(theme))

# ---- ibkr+schwab only keeps legacy context both ---------------------------
both = book(manual_lots=[], prices={"MOS": {"last": 22.88}, "CRWV": {"last": 56.22}, "VST": {"last": 133.58}})
bpos = by_sym(both)
check("no manual file lots: MOS context is both", bpos["MOS"]["context"] == "both", bpos["MOS"]["context"])
check("no AVGO when manual lots empty", "AVGO" not in bpos, str(list(bpos)))
check("IBKR-only VST context is ibkr", bpos["VST"]["context"] == "ibkr")

# ---- stale gap ------------------------------------------------------------
stale = book(manual_lots=[{
    "broker": "HSBC", "symbol": "AVGO", "shares": 2, "avg_cost": 360.74,
    "as_of": "2026-10-11", "source": "old",
}], run_on=date(2026, 11, 11))
# 2026-10-11 to 2026-11-11 is 31 days > 30
check("as_of older than 30 days flags stale gap",
      any("manual_holdings.stale" in g and "AVGO" in g for g in stale["gaps"]),
      str(stale["gaps"]))
check("stale lot marked stale true",
      by_sym(stale)["AVGO"]["brokers"][0]["stale"] is True)

# exactly 30 days is not stale
edge = book(manual_lots=[{
    "broker": "HSBC", "symbol": "AVGO", "shares": 2, "avg_cost": 360.74,
    "as_of": "2026-10-12", "source": "edge",
}], run_on=date(2026, 11, 11))
check("as_of exactly 30 days is not stale",
      edge["gaps"] == [] and by_sym(edge)["AVGO"]["brokers"][0]["stale"] is False,
      str(edge["gaps"]))

# ---- missing file is empty, not an error ---------------------------------
missing_lots, notices = mh.load_manual(Path("/tmp/master-no-such-manual-holdings.json"))
check("missing manual file yields empty lots", missing_lots == [])
check("missing manual file yields a notice", any("file_missing" in n for n in notices), str(notices))

# ---- guards ---------------------------------------------------------------
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    json.dump({"positions": [{"broker": "IBKR", "symbol": "MOS", "shares": 1,
                              "avg_cost": 20, "as_of": "2026-11-11", "source": "x"}]}, f)
    bad = Path(f.name)
try:
    try:
        mh.load_manual(bad)
        check("reject IBKR inside manual file", False, "no error")
    except mh.HoldingsError as e:
        check("reject IBKR inside manual file", "double-count" in str(e).lower() or "IBKR" in str(e), str(e))
finally:
    bad.unlink(missing_ok=True)

with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    json.dump({"positions": [
        {"broker": "HSBC", "symbol": "MOS", "shares": 1, "avg_cost": 20,
         "as_of": "2026-11-11", "source": "a"},
        {"broker": "HSBC", "symbol": "MOS", "shares": 2, "avg_cost": 21,
         "as_of": "2026-11-11", "source": "b"},
    ]}, f)
    dup = Path(f.name)
try:
    try:
        mh.load_manual(dup)
        check("reject duplicate symbol+broker", False, "no error")
    except mh.HoldingsError as e:
        check("reject duplicate symbol+broker", "duplicate" in str(e).lower(), str(e))
finally:
    dup.unlink(missing_ok=True)

expect_error_hit = False
try:
    mh.lot_from_raw({"symbol": "MOS", "shares": 0, "avg_cost": 20}, source_default="x", require_as_of=False)
except mh.HoldingsError:
    expect_error_hit = True
check("reject zero shares", expect_error_hit)

# missing price excluded from concentration
noprice = book(prices={"CRWV": {"last": 56.22}, "MOS": {"last": 22.88}, "VST": {"last": 133.58}})
check("AVGO without IBKR price has null MV", by_sym(noprice)["AVGO"]["market_value"] is None)
check("AVGO missing price is a gap",
      any("AVGO" in g and "missing_price" in g for g in noprice["gaps"]),
      str(noprice["gaps"]))
check("concentration total excludes unpriced AVGO",
      by_sym(noprice)["CRWV"]["weight_pct"] is not None
      and noprice["totals"]["market_value"] == float(
          (Decimal("26") * Decimal("56.22") + Decimal("3") * Decimal("133.58")
           + Decimal("35") * Decimal("22.88")).quantize(Decimal("0.01"))),
      str(noprice["totals"]["market_value"]))

# other single manual broker → context manual
other = book(manual_lots=[{
    "broker": "FooBank", "symbol": "AVGO", "shares": 2, "avg_cost": 360.74,
    "as_of": "2026-11-11", "source": "test",
}], live={"ibkr": [], "schwab": []}, prices={"AVGO": {"last": 341.26}})
check("non-HSBC manual-only context is manual",
      by_sym(other)["AVGO"]["context"] == "manual",
      by_sym(other)["AVGO"]["context"])

# IBKR + HSBC (no Schwab) is multi, not both
combo = book(manual_lots=[{
    "broker": "HSBC", "symbol": "VST", "shares": 1, "avg_cost": 100,
    "as_of": "2026-11-11", "source": "test",
}], live={"ibkr": [{"symbol": "VST", "qty": 3, "avg_cost": 154.18696667}], "schwab": []},
    prices={"VST": {"last": 133.58}})
check("IBKR+HSBC context is multi (not both)",
      by_sym(combo)["VST"]["context"] == "multi",
      by_sym(combo)["VST"]["context"])
check("IBKR+HSBC breakdown",
      by_sym(combo)["VST"]["breakdown"] == "VST 4（IBKR 3+HSBC 1）",
      by_sym(combo)["VST"]["breakdown"])

# ---- card validation accepts new held contexts ----------------------------
def card_ok(context, stance="HOLD"):
    c = dict(BASE)
    c["stance"] = stance
    c["entry_limit"] = None if stance != "BUY" else BASE["entry_limit"]
    if stance in {"HOLD", "SELL", "TRIM"}:
        c["upside_pct"] = None
        if stance == "HOLD":
            pass
        if stance == "TRIM":
            c["last"] = 226.0
    c["position"] = dict(BASE["position"])
    c["position"]["context"] = context
    return validate(c)


check("validate HOLD+multi is ok", card_ok("multi", "HOLD") == [])
check("validate SELL+multi is ok (held)", card_ok("multi", "SELL") == [])
check("validate SELL+hsbc is ok (held)", card_ok("hsbc", "SELL") == [])
check("validate HOLD+manual is ok", card_ok("manual", "HOLD") == [])
check("validate SELL+neither still rejected",
      any("held" in e.lower() or "position" in e.lower() for e in card_ok("neither", "SELL")))


# ---- CLI does not write watchlists / out/raw (stdout only) ----------------
# Smoke: main returns 0 and prints JSON, no files created in out/raw.
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    live_p = td / "live.json"
    price_p = td / "prices.json"
    man_p = td / "manual.json"
    live_p.write_text(json.dumps({
        "ibkr": [{"symbol": "MOS", "qty": 5, "avg_cost": 19.71526}],
        "schwab": [{"symbol": "MOS", "shares": 3, "cost_basis": 61.43}],
    }))
    price_p.write_text(json.dumps({"MOS": {"last": 22.88, "asof": "test"}}))
    man_p.write_text(json.dumps({"positions": [{
        "broker": "HSBC", "symbol": "MOS", "shares": 27, "avg_cost": 20.428,
        "as_of": "2026-11-11", "source": "Veit chat 2026-11-11",
    }]}))
    # run CLI; capture via function
    import io
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        rc = mh.main(["--manual", str(man_p), "--live", str(live_p),
                      "--prices", str(price_p), "--asof", "2026-11-11"])
    finally:
        sys.stdout = old
    check("CLI exit 0", rc == 0, str(rc))
    payload = json.loads(buf.getvalue())
    check("CLI prints merged MOS 35", payload["positions"][0]["qty"] == 35)
    check("CLI created no sibling files besides inputs",
          sorted(p.name for p in td.iterdir()) == ["live.json", "manual.json", "prices.json"],
          str(list(td.iterdir())))


def main() -> int:
    failed = 0
    for name, ok, detail in results:
        mark = "OK " if ok else "FAIL"
        extra = f" — {detail}" if detail else ""
        print(f"  {mark} {name}{extra}")
        if not ok:
            failed += 1
    print(f"\ntest_holdings_merge: {len(results) - failed}/{len(results)} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
