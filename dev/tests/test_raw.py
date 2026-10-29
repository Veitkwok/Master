#!/usr/bin/env python3
"""Raw log tests: atomic, valid JSON, collision-proof filename."""

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("worker", ROOT / "skills/finance-master/scripts/deepseek_analyze.py")
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)  # type: ignore[union-attr]

tmp = Path(tempfile.mkdtemp(dir=ROOT / "dev" / "tests"))
worker.OUT_DEFAULT = tmp
worker.write_raw({"job_id": "20261029-holdings-0826", "routine": "",
                  "asof": "2026-10-29T08:26:18+08:00",
                  "pack": {"routine": "holdings", "symbols": {}}},
                 {"schema": "master.deepseek.result/v1", "tickers": [{"symbol": "CEG"}]}, 0)
worker.write_raw({"job_id": "20261029-holdings-0826", "asof": "", "pack": {}},
                 {"schema": "master.deepseek.result/v1", "tickers": []}, 0)
raw = tmp / "raw"
files = sorted(p.name for p in raw.iterdir())
json_files = [p for p in raw.iterdir() if p.name.endswith(".worker.stdout.json")]
ok = (len(json_files) == 2
      and all(name.endswith((".worker.stdout.json", ".worker.exit", ".worker.meta.json")) for name in files)
      and all("holdings" in p.name for p in json_files))
try:
    payloads = [json.loads(p.read_text(encoding="utf-8")) for p in json_files]
    ok = ok and any(pl.get("tickers") and pl["tickers"][0].get("symbol") == "CEG"
                    for pl in payloads)
except Exception:
    ok = False
for p in sorted(raw.iterdir(), reverse=True):
    p.unlink()
raw.rmdir()
tmp.rmdir()
print(("PASS " if ok else "FAIL ") + "raw file valid/atomic/distinct")
print("1/1 passed" if ok else "0/1 passed")
raise SystemExit(0 if ok else 1)
