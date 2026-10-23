#!/usr/bin/env python3
"""Tests for the valuation-input gate (worker exit 8)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "finance-master" / "scripts" / "deepseek_analyze.py"
TMP = ROOT / ".jobcheck-test.json"


def run(job: dict) -> tuple[int, dict]:
    TMP.write_text(json.dumps(job), encoding="utf-8")
    try:
        p = subprocess.run([sys.executable, str(SCRIPT), "--check-job", "--pack", str(TMP)],
                           capture_output=True, text=True)
    finally:
        TMP.unlink(missing_ok=True)
    try:
        out = json.loads(p.stdout)
    except json.JSONDecodeError:
        out = {"raw": p.stdout, "stderr": p.stderr}
    return p.returncode, out


def job(symbols: dict) -> dict:
    return {"schema": "master.deepseek.job/v1", "job_id": "t", "mode": "routine",
            "pack": {"tickers": list(symbols), "symbols": symbols}}


GOOD_STOCK = {
    "security_type": "STK",
    "quote": {"last": 100.0},
    "fundamentals_web": {
        "shares_diluted": 1_000_000,
        "net_debt": 0,
        "revenue_ttm": 500_000_000,
        "fcf_ttm": 80_000_000,
        "eps_ttm": 2.0,
        "peers": [
            {"symbol": "A", "multiples": {"pe": 20.0}},
            {"symbol": "B", "multiples": {"ev_sales": 3.0}},
            {"symbol": "C", "multiples": {"ev_ebitda": 9.0}},
        ],
    },
}

COMPS_STOCK = {
    "security_type": "STK",
    "quote": {"last": 100.0},
    "fundamentals_web": {
        "shares_diluted": 1_000_000,
        "net_debt": 10_000_000,
        "revenue_ttm": 500_000_000,
        "peers": [
            {"symbol": "A", "multiples": {"ev_sales": 3.0}},
            {"symbol": "B", "multiples": {"ev_sales": 4.0}},
            {"symbol": "C", "multiples": {"ev_sales": 5.0}},
        ],
    },
}


def main() -> int:
    cases = []

    rc, out = run(job({"VST": {"security_type": "STK", "quote": {"last": 100.0}}}))
    cases.append(("incomplete stock -> 8", rc == 8 and out.get("status") == "incomplete"))

    rc, out = run(job({"VST": GOOD_STOCK}))
    cases.append(("DCF route -> 0", rc == 0 and out.get("status") == "ok"))

    rc, out = run(job({"MOS": COMPS_STOCK}))
    cases.append(("comps route -> 0", rc == 0 and out.get("status") == "ok"))

    rc, out = run(job({"SILJ": {"security_type": "ETF", "quote": {"last": 10.0}}}))
    cases.append(("ETF without NAV -> 8", rc == 8 and out.get("status") == "incomplete"))

    rc, out = run(job({"SILJ": {"security_type": "ETF", "quote": {"last": 10.0},
                                "fundamentals_web": {"etf_issuer": {"nav": 9.8}}}}))
    cases.append(("ETF with NAV -> 0", rc == 0 and out.get("status") == "ok"))

    bad = {"symbols": {"VST": {"security_type": "STK", "quote": {"last": 100.0},
                               "fundamentals_web": {"shares_diluted": 1, "net_debt": 0,
                                                    "eps_ttm": 1, "peers": ["AMD", "NVDA"]}}}}
    rc, out = run({"schema": "master.deepseek.job/v1", "pack": {**bad, "tickers": ["VST"]}})
    cases.append(("peer strings (old shape) -> 8", rc == 8))

    # real sample job should pass the gate
    sample = json.loads((ROOT / "dev" / "samples" / "job.sample.json").read_text(encoding="utf-8"))
    TMP.write_text(json.dumps(sample), encoding="utf-8")
    try:
        p = subprocess.run([sys.executable, str(SCRIPT), "--check-job", "--pack", str(TMP)],
                           capture_output=True, text=True)
    finally:
        TMP.unlink(missing_ok=True)
    cases.append(("sample job -> 0", p.returncode == 0))

    failures = 0
    for name, ok in cases:
        print(("PASS " if ok else "FAIL ") + name)
        failures += 0 if ok else 1
    print(f"\n{len(cases)-failures}/{len(cases)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
