#!/usr/bin/env python3
"""Earnings preview/recap wiring (v1.0.31).

    python3 dev/tests/test_earnings.py

Covers: conditional system files (no earnings -> system unchanged), deterministic
compute_earnings (beat/miss, guidance, reaction, exit_flags), card validation with
and without the optional earnings block.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dev"))
from validate_card import validate  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "worker", ROOT / "skills/finance-master/scripts/deepseek_analyze.py")
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)  # type: ignore[union-attr]
worker.SKILL = ROOT / "skills" / "finance-master"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_cards import BASE  # noqa: E402

PREVIEW_GUIDE = "earnings-preview/GUIDE.md"
RECAP_GUIDE = "earnings-recap/GUIDE.md"

results: list[tuple[str, bool]] = []


def check(name: str, ok: bool) -> None:
    results.append((name, bool(ok)))


def files_in(system: str) -> list[str]:
    return [line[5:-4] for line in system.splitlines() if line.startswith("<!-- ")]


# ---- conditional system loading -------------------------------------------
plain, plain_sha = worker.build_system("routine")
legacy = "".join(f"\n\n<!-- {rel} -->\n\n" + (worker.SKILL / rel).read_text(encoding="utf-8")
                 for rel in worker.SYSTEM_FILES)
check("no earnings: system identical to fixed list (cache prefix unchanged)", plain == legacy)
check("no earnings: no earnings files loaded",
      not any("earnings" in f for f in files_in(plain)))
pre, _ = worker.build_system("routine", {"preview"})
check("preview: loads preview GUIDE + worker_earnings, not recap",
      any(f.endswith(PREVIEW_GUIDE) for f in files_in(pre))
      and not any(f.endswith(RECAP_GUIDE) for f in files_in(pre))
      and files_in(pre)[-1] == worker.EARNINGS_WORKER_FILE)
both, _ = worker.build_system("routine", {"recap", "preview"})
check("both: deterministic order preview -> recap -> worker_earnings",
      files_in(both)[-3:] == [worker.EARNINGS_EXTRA_FILES["preview"][0],
                               worker.EARNINGS_EXTRA_FILES["recap"][0],
                               worker.EARNINGS_WORKER_FILE])
check("earnings system keeps the plain system as prefix", both.startswith(plain))
check("unknown phase ignored", worker.build_system("routine", {"foo"})[0] == plain)

# ---- flags + deterministic arithmetic --------------------------------------
PACK = {"tickers": ["AAA", "BBB", "CCC"], "symbols": {
    "AAA": {"earnings": {
        "phase": "recap", "report_date": "2026-11-10", "timing": "AMC", "quarter": "Q3 2026",
        "source_url": "https://ir.example.com/q3",
        "actual": {"eps": -0.20, "revenue": 1_300_000_000},
        "estimate": {"eps": -0.25, "revenue": 1_400_000_000},
        "guidance": [{"item": "FY revenue", "new_low": 5.0e9, "new_high": 5.2e9,
                      "prior_low": 5.1e9, "prior_high": 5.3e9}],
        "price_reaction": {"prior_close": 50.0, "last": 45.0, "session": "post"}}},
    "BBB": {"earnings": {"phase": "preview", "report_date": "2026-11-14",
                         "source_url": "https://ir.example.com/date",
                         "consensus": {"eps": 1.1, "revenue": None, "asof": "2026-11-09"}}},
    "CCC": {"quote": {"last": 10.0}},
}}
check("earnings_flags picks only flagged tickers",
      worker.earnings_flags(PACK) == {"AAA": "recap", "BBB": "preview"})
ce = worker.compute_earnings(PACK)
a = ce.get("AAA", {})
check("recap: negative EPS beat uses |estimate|",
      a.get("eps", {}).get("label") == "beat" and a["eps"]["variance_pct"] == 20.0)
check("recap: revenue miss variance",
      a.get("revenue", {}).get("label") == "miss" and a["revenue"]["variance_pct"] == -7.14)
check("recap: guidance lowered by midpoint",
      a.get("guidance", {}).get("direction") == "lowered"
      and a["guidance"]["items"][0]["basis"] == "computed_midpoint")
check("recap: price reaction pct", (a.get("price_reaction") or {}).get("pct") == -10.0)
check("recap: exit_flags", a.get("exit_flags") == {
    "eps_miss": False, "revenue_miss": True, "guide_lowered": True})
b = ce.get("BBB", {})
check("preview: consensus echoed, missing revenue is a gap",
      b.get("consensus", {}).get("eps") == 1.1
      and "earnings.consensus.revenue" in b.get("fields_gap", []))
check("non-flagged ticker absent", "CCC" not in ce)
TOL = worker.compute_earnings({"symbols": {"T": {"earnings": {
    "phase": "recap", "report_date": "d", "source_url": "u",
    "actual": {"eps": 1.00, "revenue": 100.0},
    "estimate": {"eps": 1.005, "revenue": 100.2}}}}})["T"]
check("tolerance: eps -0.5% is inline technical_miss",
      TOL["eps"]["label"] == "inline" and TOL["eps"]["technical_miss"] is True
      and TOL["eps"]["variance_pct"] == -0.5)
check("tolerance: within-band revenue is inline",
      TOL["revenue"]["label"] == "inline" and TOL["revenue"]["technical_miss"] is True)
check("tolerance: material miss still exit true", worker.compute_earnings({
    "symbols": {"M": {"earnings": {"phase": "recap", "report_date": "d", "source_url": "u",
        "actual": {"eps": 1.00}, "estimate": {"eps": 1.02}}}}})["M"]["exit_flags"]["eps_miss"] is True)
src = worker.compute_earnings({"symbols": {"X": {"earnings": {
    "phase": "recap", "report_date": "d", "source_url": "u",
    "guidance": {"item": "capex", "direction": "maintained"}}}}})["X"]
check("recap: sourced guidance direction passthrough",
      src["guidance"]["direction"] == "maintained"
      and src["guidance"]["items"][0]["basis"] == "pack_sourced")

# ---- card validation --------------------------------------------------------
HOLD = dict(BASE, stance="HOLD", routine="holdings", entry_limit=None)
check("card without earnings still valid", validate(HOLD) == [])
REC = {"phase": "recap", "report_date": "2026-11-10", "timing": "AMC",
       "source_url": "https://ir.example.com/q3",
       "eps": {"actual": -0.20, "estimate": -0.25, "variance_pct": 20.0, "label": "beat"},
       "revenue": {"actual": 1.3e9, "estimate": 1.4e9, "variance_pct": -7.14, "label": "miss"},
       "guidance_direction": "lowered",
       "exit_flags": {"eps_miss": False, "revenue_miss": True, "guide_lowered": True},
       "override_exit_hit": True,
       "override_note": "覆盖退出条件『指引下调』已出现，需你在对话里决定"}
check("card with recap earnings valid", validate(dict(HOLD, earnings=REC)) == [])
check("SELL card with recap earnings valid",
      validate(dict(HOLD, stance="SELL", trigger="invalidation", earnings=REC)) == [])
PRE = {"phase": "preview", "report_date": "2026-11-14", "timing": "BMO",
       "source_url": "https://ir.example.com/date",
       "consensus": {"eps": 1.1, "revenue": None, "asof": "2026-11-09"}}
check("card with preview earnings valid", validate(dict(HOLD, earnings=PRE)) == [])
check("neg: label contradicts numbers",
      validate(dict(HOLD, earnings=dict(REC, eps=dict(REC["eps"], label="miss"),
                                        exit_flags=dict(REC["exit_flags"], eps_miss=True)))) != [])
check("neg: exit flag hidden (guide lowered but flag false)",
      validate(dict(HOLD, earnings=dict(REC, exit_flags=dict(REC["exit_flags"],
                                                             guide_lowered=False)))) != [])
check("neg: unsourced earnings", validate(dict(HOLD, earnings=dict(REC, source_url=None))) != [])
check("neg: preview carrying actuals", validate(dict(HOLD, earnings=dict(PRE, eps=REC["eps"]))) != [])
check("neg: bad phase", validate(dict(HOLD, earnings={"phase": "deep"})) != [])
check("neg: override_exit_hit without note",
      validate(dict(HOLD, earnings=dict(REC, override_note=None))) != [])
check("earnings never unlocks BUY gates (C still blocked)",
      validate(dict(BASE, risk=dict(BASE["risk"], confidence="C"), earnings=PRE)) != [])


# ---- end-to-end with a mocked API (temp out dir; never touches out/raw) ----
import io, json, tempfile, shutil, contextlib  # noqa: E402


def _fake_ok(symbols_out):
    def fake(key, body, timeout):
        fake.systems.append(body["messages"][0]["content"])
        content = json.dumps({"status": "ok", "tickers": symbols_out})
        return {"choices": [{"message": {"content": content}, "finish_reason": "stop"}],
                "usage": {}, "id": "x"}, 200
    fake.systems = []
    return fake


GOOD_FW = {"shares_diluted": 1e6, "net_debt": 0, "revenue_ttm": 5e8, "fcf_ttm": 8e7,
           "eps_ttm": 2.0, "peers": [{"symbol": s, "multiples": {"pe": v}}
                                     for s, v in (("P1", 18.0), ("P2", 20.0), ("P3", 22.0))]}
TK = {"confidence_block": {"grade": "C"}, "challenge_nodes": []}
tmp = Path(tempfile.mkdtemp(dir=Path(__file__).resolve().parent))
orig_out, orig_http = worker.OUT_DEFAULT, worker.http_call
try:
    worker.OUT_DEFAULT = tmp
    for label, sym_pack, wk_out, expect_files, expect_keys in (
        ("e2e no earnings: stdout shape unchanged, plain system",
         {"AAA": {"quote": {"last": 40.0}, "fundamentals_web": GOOD_FW}},
         [dict(TK, symbol="AAA")], False, False),
        ("e2e recap: earnings files loaded, stdout carries earnings + computed_earnings",
         {"AAA": {"quote": {"last": 40.0}, "fundamentals_web": GOOD_FW,
                  "earnings": PACK["symbols"]["AAA"]["earnings"]}},
         [dict(TK, symbol="AAA", earnings={"phase": "recap", "status": "ok"})], True, True),
    ):
        fake = _fake_ok(wk_out)
        worker.http_call = fake
        job = {"job_id": "20261111-holdings-0830", "routine": "holdings", "mode": "routine",
               "pack": {"tickers": list(sym_pack), "symbols": sym_pack}}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = worker.run_analysis(job, "k")
        out = json.loads(buf.getvalue())
        t0 = out["tickers"][0]
        loaded = "earnings-recap/GUIDE.md" in fake.systems[0]
        keys = "computed_earnings" in t0 and "earnings" in t0
        ok = rc == 0 and loaded == expect_files and keys == expect_keys
        if expect_keys:
            ok = ok and t0["computed_earnings"]["exit_flags"]["guide_lowered"] is True
        check(label, ok)
    # flagged but worker omitted earnings -> warning, not failure
    fake = _fake_ok([dict(TK, symbol="AAA")])
    worker.http_call = fake
    job = {"job_id": "20261111-holdings-0830", "routine": "holdings", "mode": "routine",
           "pack": {"tickers": ["AAA"], "symbols": {"AAA": {
               "quote": {"last": 40.0}, "fundamentals_web": GOOD_FW,
               "earnings": PACK["symbols"]["BBB"]["earnings"]}}}}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
        rc = worker.run_analysis(job, "k")
    out = json.loads(buf.getvalue())
    check("e2e flagged but worker omitted earnings -> warning only",
          rc == 0 and any("no earnings block" in w for w in out.get("warnings", [])))
finally:
    worker.OUT_DEFAULT, worker.http_call = orig_out, orig_http
    shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    failures = 0
    for name, ok in results:
        print(("PASS " if ok else "FAIL ") + name)
        failures += not ok
    print(f"\n{len(results) - failures}/{len(results)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
