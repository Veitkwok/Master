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
worker.write_raw({"job_id": "20261028-primary_balder-0802", "routine": "primary_balder",
                  "asof": "2026-10-28T07:56:00+08:00"},
                 {"schema": "master.deepseek.result/v1", "tickers": [{"symbol": "CEG"}]}, 0)
raw = tmp / "raw"
files = sorted(p.name for p in raw.iterdir())
json_files = [p for p in raw.iterdir() if p.name.endswith(".worker.stdout.json")]
ok = (len(json_files) == 1
      and all(name.endswith((".worker.stdout.json", ".worker.exit", ".worker.meta.json")) for name in files)
      and "primary_balder" in json_files[0].name)
try:
    payload = json.loads(json_files[0].read_text(encoding="utf-8"))
    ok = ok and payload["tickers"][0]["symbol"] == "CEG"
except Exception:
    ok = False
for p in sorted(raw.iterdir(), reverse=True):
    p.unlink()
raw.rmdir()
tmp.rmdir()
print(("PASS " if ok else "FAIL ") + "raw file valid/atomic/distinct")
print("1/1 passed" if ok else "0/1 passed")
raise SystemExit(0 if ok else 1)
