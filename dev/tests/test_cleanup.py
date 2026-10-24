#!/usr/bin/env python3
"""Optional gap/limiting cleanup tests (social_x / WACC variants)."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("worker", ROOT / "skills/finance-master/scripts/deepseek_analyze.py")
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)  # type: ignore[union-attr]

result = {"tickers": [
    {"symbol": "NVDA", "fields_gap": ["wacc", "fundamentals_web.wacc", "dcf.wacc",
                                      "social_x.posts", "peers.multiples"],
     "limiting": ["无 WACC 来源页，用引擎默认", "负 FCF"],
     "valuation": {"fields_gap": ["数据包未给 WACC", "peers.multiples"]}},
    {"symbol": "MOS", "fields_gap": [], "limiting": []},
]}
worker.clean_optional(result)
gaps = result["tickers"][0]["fields_gap"]
limiting = result["tickers"][0]["limiting"]
nested = result["tickers"][0]["valuation"]["fields_gap"]
ok = (gaps == ["peers.multiples"] and limiting == ["负 FCF"]
      and nested == ["peers.multiples"] and result["warnings"])
print(("PASS " if ok else "FAIL ") + "cleanup removes wacc/social_x variants")
print("1/1 passed" if ok else "0/1 passed")
raise SystemExit(0 if ok else 1)
