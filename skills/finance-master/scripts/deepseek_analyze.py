#!/usr/bin/env python3
"""DeepSeek analysis worker for the finance-master Master pack.

This is the ONE fixed command the Grok Bot routine runs:

    /usr/bin/python3 -I -B /workspace/master/scripts/deepseek_analyze.py

with working directory /workspace/master. It reads the current job, calls
DeepSeek once, writes full results to out/current.result.json, and prints a
compact JSON payload (the Bot reads only this; long analysis stays on disk).

Local / manual usage:

    python3 deepseek_analyze.py --pack dev/samples/job.sample.json
    python3 deepseek_analyze.py --selftest
    python3 deepseek_analyze.py --selftest --ping
    python3 deepseek_analyze.py --dump-system

Environment overrides (optional):
    MASTER_WORKSPACE        default /workspace/master (or $HOME/master fallback)
    MASTER_JOB              default <workspace>/jobs/current.json
    MASTER_OUT_DIR          default <workspace>/out
    MASTER_SECRET           default <workspace>/.secrets/deepseek.key
    DEEPSEEK_API_KEY        fallback if the key file is absent
    DEEPSEEK_BASE_URL       default https://api.deepseek.com
    DEEPSEEK_MODEL          override model
    DEEPSEEK_THINKING       on|off (default: per job mode)
    DEEPSEEK_TIMEOUT        seconds (default 240)

Earnings (v1.0.31): when a ticker in the pack carries
symbols.<SYM>.earnings.phase = preview|recap, the matching earnings GUIDE plus
scripts/worker_earnings.md are appended after the fixed system files, and each
flagged ticker gets a deterministic `computed_earnings`. Jobs without that flag
build exactly the same system prompt as before.

Exit codes (the Bot acts on these):
    0 ok | 2 config/auth | 3 network | 4 invalid JSON output |
    5 output truncated | 6 rate-limited/5xx after retries | 7 timeout
    8 valuation inputs incomplete (Bot should collect more, rewrite job, rerun)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
from datetime import datetime
import urllib.error
import urllib.request
import uuid
from pathlib import Path

def _resolve_skill_root() -> Path:
    """Works both inside the skill pack and from a copied script under /workspace."""
    env = os.environ.get("MASTER_SKILL_ROOT", "").strip()
    candidates = [Path(env)] if env else []
    here = Path(__file__).resolve().parents[1]
    candidates += [
        here,
        Path(os.environ.get("MASTER_WORKSPACE", "/workspace/master")) / "skill",
        Path.home() / "agent-data" / "workflows" / "finance-master",
    ]
    for cand in candidates:
        if (cand / "scripts" / "worker_prompt.md").is_file() and (cand / "references").is_dir():
            return cand
    return here


SKILL = _resolve_skill_root()
WORKSPACE = Path(os.environ.get("MASTER_WORKSPACE", "/workspace/master"))
JOB_DEFAULT = WORKSPACE / "jobs" / "current.json"
OUT_DEFAULT = Path(os.environ.get("MASTER_OUT_DIR", str(WORKSPACE / "out")))
SECRET_DEFAULT = Path(os.environ.get("MASTER_SECRET", str(WORKSPACE / ".secrets" / "deepseek.key")))

SYSTEM_FILES = [
    "scripts/worker_prompt.md",
    "references/engine/sherlock/GUIDE.md",
    "references/engine/sherlock/references/full-engine.md",
    "references/engine/sherlock/references/l2-confidence-contract.md",
    "references/engine/sherlock/references/confidence-examples.md",
    "references/engine/modules/company-valuation/GUIDE.md",
    "references/engine/modules/company-valuation/references/dcf.md",
    "references/engine/modules/company-valuation/references/relative_valuation.md",
    "references/engine/modules/trap-detector/GUIDE.md",
    "references/engine/modules/trap-detector/references/eight-signals.md",
    "references/engine/docs/reference/priced-in-checklist.md",
    "references/contracts/book-and-overlaps.md",
    "references/contracts/confidence.md",
]
DEEP_EXTRA_FILES = [
    "references/engine/modules/deep-analysis/GUIDE.md",
    "references/engine/docs/reference/research-bias-checklist.md",
]
# Loaded ONLY when the pack flags a ticker with symbols.<SYM>.earnings.phase
# (holdings earnings window, v1.0.31). Appended after the fixed files so the
# cached system prefix of non-earnings jobs is unchanged.
EARNINGS_PHASES = ("preview", "recap")
EARNINGS_EXTRA_FILES = {
    "preview": ["references/engine/modules/earnings-preview/GUIDE.md"],
    "recap": ["references/engine/modules/earnings-recap/GUIDE.md"],
}
EARNINGS_WORKER_FILE = "scripts/worker_earnings.md"
GUIDANCE_DIRECTIONS = {"raised", "maintained", "lowered", "none"}
EARNINGS_TOLERANCE_EPS_PCT = float(os.environ.get("EARNINGS_EPS_TOLERANCE_PCT", "1.0"))
EARNINGS_TOLERANCE_REVENUE_PCT = float(os.environ.get("EARNINGS_REVENUE_TOLERANCE_PCT", "0.5"))

MAX_PACK_CHARS = 400_000
ANCHOR = json.dumps(
    {"protocol": "master.deepseek/v1",
     "instruction": "Read the system contract. The job follows in the next user message. "
                    "Do not restate the contract."},
    ensure_ascii=False,
)
MODEL = {"routine": "deepseek-flash", "deep": "deepseek-flash"}  # Pro only via DEEPSEEK_MODEL
MAX_TOKENS = {"routine": 16000, "deep": 48000}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_key() -> str:
    if SECRET_DEFAULT.is_file():
        return SECRET_DEFAULT.read_text(encoding="utf-8").strip()
    return os.environ.get("DEEPSEEK_API_KEY", "").strip()


def build_system(mode: str, earnings_phases=()) -> tuple[str, str]:
    files = list(SYSTEM_FILES) + (DEEP_EXTRA_FILES if mode == "deep" else [])
    phases = [ph for ph in EARNINGS_PHASES if ph in set(earnings_phases or ())]
    for ph in phases:
        files += EARNINGS_EXTRA_FILES[ph]
    if phases:
        files.append(EARNINGS_WORKER_FILE)
    parts = []
    for rel in files:
        path = SKILL / rel
        if not path.is_file():
            raise FileNotFoundError(f"missing system file: {path}")
        parts.append(f"\n\n<!-- {rel} -->\n\n")
        parts.append(path.read_text(encoding="utf-8"))
    system = "".join(parts)
    return system, sha256(system)


def load_job(pack_path: str | None) -> dict:
    if pack_path and pack_path != "-":
        raw = Path(pack_path).read_text(encoding="utf-8")
    else:
        job_path = Path(os.environ.get("MASTER_JOB", str(JOB_DEFAULT)))
        if not job_path.is_file():
            raise FileNotFoundError(f"job file not found: {job_path}")
        raw = job_path.read_text(encoding="utf-8")
    if len(raw) > MAX_PACK_CHARS:
        raise ValueError(f"job {len(raw)} chars > {MAX_PACK_CHARS}")
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"job is not valid JSON: {exc}")
    if not isinstance(obj, dict):
        raise ValueError("job must be a JSON object")
    return obj


def job_mode(job: dict) -> str:
    mode = str(job.get("mode") or job.get("worker_mode") or "routine").lower()
    return "deep" if mode == "deep" else "routine"


def job_payload(job: dict) -> dict:
    """The Bot writes the data pack either under `pack` or directly in the job."""
    if isinstance(job.get("pack"), dict):
        return job["pack"]
    return {k: v for k, v in job.items()
            if k not in {"schema", "job_id", "mode", "asof", "locale", "constraints"}}


def compact(obj: object) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _tickers_map(pack: dict) -> dict:
    if isinstance(pack.get("symbols"), dict):
        return pack["symbols"]
    if isinstance(pack.get("tickers"), dict):
        return pack["tickers"]
    if isinstance(pack.get("tickers"), list):
        out = {}
        for sym in pack["tickers"]:
            if isinstance(sym, str):
                out[sym] = (pack.get("symbols") or {}).get(sym, {})
        return out
    return {}


def _num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _peer_values(peers, key: str) -> list[float]:
    vals = []
    for peer in peers or []:
        if isinstance(peer, dict):
            mult = peer.get("multiples") or {}
            v = mult.get(key)
            if _num(v):
                vals.append(float(v))
    return vals


def _has_dcf_route(fw: dict) -> bool:
    fcf = fw.get("fcf_ttm")
    return (
        _num(fcf) and fcf > 0
        and _num(fw.get("shares_diluted")) and fw.get("shares_diluted", 0) > 0
        and _num(fw.get("net_debt"))
        and _num(fw.get("revenue_ttm")) and fw.get("revenue_ttm", 0) > 0
    )


def _comp_routes(fw: dict) -> list[str]:
    peers = fw.get("peers") if isinstance(fw.get("peers"), list) else []
    routes = []
    if _num(fw.get("eps_ttm")) and len(_peer_values(peers, "pe")) >= 3:
        routes.append("pe")
    if _num(fw.get("revenue_ttm")) and len(_peer_values(peers, "ev_sales")) >= 3:
        routes.append("ev_sales")
    if _num(fw.get("ebitda_ttm")) and len(_peer_values(peers, "ev_ebitda")) >= 3:
        routes.append("ev_ebitda")
    return routes


def _pct(values: list[float], q: float) -> float:
    vals = sorted(values)
    if not vals:
        return 0.0
    if len(vals) == 1:
        return float(vals[0])
    pos = (len(vals) - 1) * q
    lo, hi = int(pos), min(int(pos) + 1, len(vals) - 1)
    frac = pos - lo
    return float(vals[lo] * (1 - frac) + vals[hi] * frac)


def compute_comps(pack: dict) -> dict:
    """Deterministic comps fallback computed from the pack (not the model).

    Used when the worker refuses/omits comps_range. Values are traceable:
    every implied price comes from peer multiples + the target's own metric.
    """
    out: dict = {}
    for sym, t in _tickers_map(pack).items():
        if not isinstance(t, dict) or str(t.get("security_type", "")).upper() == "ETF":
            continue
        fw = t.get("fundamentals_web") or {}
        quote = t.get("quote") or {}
        last = quote.get("last", t.get("last"))
        shares = fw.get("shares_diluted")
        net_debt = fw.get("net_debt")
        peers = fw.get("peers") if isinstance(fw.get("peers"), list) else []
        lenses = []

        def try_lens(name: str, metric, key: str, mode: str) -> None:
            if not _num(metric) or metric == 0:
                return
            mults = _peer_values(peers, key)
            used = [p.get("symbol") for p in peers
                    if isinstance(p, dict) and _num((p.get("multiples") or {}).get(key))]
            if len(mults) < 3:
                return
            med = _pct(mults, 0.5)
            if mode == "pe":
                base = med * metric
            else:  # EV-based multiples
                if not (_num(shares) and shares > 0) or not _num(net_debt):
                    return
                ev = med * metric
                base = (ev - net_debt) / shares
            if not _num(base) or base <= 0:
                return
            low_mult, high_mult = _pct(mults, 0.25), _pct(mults, 0.75)
            if mode == "pe":
                low, high = low_mult * metric, high_mult * metric
            else:
                low = ((low_mult * metric) - net_debt) / shares
                high = ((high_mult * metric) - net_debt) / shares
            ratio = (max(mults) / min(mults)) if min(mults) > 0 else 999
            width = ((high - low) / base) if base > 0 else 999
            last0 = last if _num(last) and last > 0 else None
            upside = (base / last0 - 1) if last0 else None
            quality = "ok"
            cap = "B"
            if ratio > 3:
                quality, cap = "wide", "B"
            if width > 1.0 or ratio > 10 or (upside is not None and abs(upside) > 0.5):
                quality, cap = "very_wide", "C"
            # a target more than 5x (or less than 0.2x) the live price is not usable
            if last0 and (base / last0 > 5 or base / last0 < 0.2):
                quality, cap = "insufficient", "C"
            lenses.append({
                "lens": name,
                "metric": key,
                "base": round(base, 2),
                "low": round(low, 2),
                "high": round(high, 2),
                "peers_used": used,
                "peers_count": len(mults),
                "median_multiple": round(med, 4),
                "dispersion_ratio": round(ratio, 2),
                "width_ratio": round(width, 3),
                "upside_pct": round(upside * 100, 1) if upside is not None else None,
                "quality": quality,
                "confidence_cap": cap,
                "usable": quality != "insufficient",
            })

        try_lens("pe", fw.get("eps_ttm"), "pe", "pe")
        try_lens("ev_sales", fw.get("revenue_ttm"), "ev_sales", "ev")
        try_lens("ev_ebitda", fw.get("ebitda_ttm"), "ev_ebitda", "ev")
        if lenses:
            rank = {"ok": 0, "wide": 1, "very_wide": 2, "insufficient": 3}
            lenses.sort(key=lambda x: (
                rank[x["quality"]],
                abs(x.get("upside_pct") or 999),
                abs(x["width_ratio"]),
            ))
            best = dict(lenses[0])
            out[sym] = best
    return out


def earnings_flags(pack: dict) -> dict:
    """{SYM: phase} for tickers whose pack carries earnings.phase preview|recap."""
    flags = {}
    for sym, t in _tickers_map(pack).items():
        e = t.get("earnings") if isinstance(t, dict) else None
        if isinstance(e, dict) and e.get("phase") in EARNINGS_PHASES:
            flags[sym] = e["phase"]
    return flags


def _range_mid(lo, hi):
    if _num(lo) and _num(hi):
        return (float(lo) + float(hi)) / 2
    if _num(lo):
        return float(lo)
    if _num(hi):
        return float(hi)
    return None


def _guidance_items(g) -> list[dict]:
    if isinstance(g, dict):
        return [g]
    if isinstance(g, list):
        return [x for x in g if isinstance(x, dict)]
    return []


def compute_earnings(pack: dict) -> dict:
    """Deterministic earnings arithmetic from the pack (not the model).

    recap: actual vs estimate variance + label (sign only, no band), guidance
    direction (numeric midpoint new vs prior, else the pack's sourced direction),
    price reaction from pack prices, and exit_flags for the human/override check.
    preview: echoes the sourced consensus only. Missing inputs -> null + fields_gap.
    """
    out: dict = {}
    for sym, t in _tickers_map(pack).items():
        e = t.get("earnings") if isinstance(t, dict) else None
        if not isinstance(e, dict) or e.get("phase") not in EARNINGS_PHASES:
            continue
        phase = e["phase"]
        gaps: list[str] = []
        res: dict = {
            "phase": phase,
            "report_date": e.get("report_date"),
            "timing": e.get("timing"),
            "quarter": e.get("quarter"),
            "source_url": e.get("source_url"),
        }
        if not e.get("report_date"):
            gaps.append("earnings.report_date")
        if not e.get("source_url"):
            gaps.append("earnings.source_url")
        if phase == "preview":
            cons = e.get("consensus") or {}
            res["consensus"] = {
                "eps": cons.get("eps") if _num(cons.get("eps")) else None,
                "revenue": cons.get("revenue") if _num(cons.get("revenue")) else None,
                "asof": cons.get("asof"),
                "source_url": cons.get("source_url"),
            }
            for k in ("eps", "revenue"):
                if res["consensus"][k] is None:
                    gaps.append(f"earnings.consensus.{k}")
        else:
            actual = e.get("actual") or {}
            est = e.get("estimate") or {}
            for k in ("eps", "revenue"):
                a, b = actual.get(k), est.get(k)
                if _num(a) and _num(b) and b != 0:
                    var = (a - b) / abs(b) * 100
                    tol = (EARNINGS_TOLERANCE_EPS_PCT if k == "eps"
                           else EARNINGS_TOLERANCE_REVENUE_PCT)
                    if var > tol:
                        label = "beat"
                    elif var < -tol:
                        label = "miss"
                    else:
                        label = "inline"
                    technical = bool(a < b and label == "inline")
                    res[k] = {"actual": a, "estimate": b, "variance_pct": round(var, 2),
                              "label": label, "technical_miss": technical}
                else:
                    res[k] = None
                    gaps.append(f"earnings.actual/estimate.{k}")
            items = []
            for g in _guidance_items(e.get("guidance")):
                new_mid = _range_mid(g.get("new_low"), g.get("new_high"))
                prior_mid = _range_mid(g.get("prior_low"), g.get("prior_high"))
                if new_mid is not None and prior_mid is not None:
                    direction = ("raised" if new_mid > prior_mid
                                 else "lowered" if new_mid < prior_mid else "maintained")
                    basis = "computed_midpoint"
                elif g.get("direction") in GUIDANCE_DIRECTIONS:
                    direction, basis = g["direction"], "pack_sourced"
                else:
                    direction, basis = None, None
                items.append({"item": g.get("item"), "direction": direction, "basis": basis,
                              "new_mid": new_mid, "prior_mid": prior_mid})
            dirs = [i["direction"] for i in items if i["direction"]]
            if "lowered" in dirs:
                overall = "lowered"
            elif "raised" in dirs:
                overall = "raised"
            elif "maintained" in dirs:
                overall = "maintained"
            elif "none" in dirs:
                overall = "none"
            else:
                overall = None
                gaps.append("earnings.guidance")
            res["guidance"] = {"direction": overall, "items": items}
            pr = e.get("price_reaction") or {}
            base, last = pr.get("prior_close"), pr.get("last")
            if _num(base) and _num(last) and base > 0:
                res["price_reaction"] = {"prior_close": base, "last": last,
                                         "pct": round((last / base - 1) * 100, 2),
                                         "session": pr.get("session"), "asof": pr.get("asof")}
            else:
                res["price_reaction"] = None
                gaps.append("earnings.price_reaction")
            res["exit_flags"] = {
                "eps_miss": (res["eps"]["label"] == "miss") if res.get("eps") else None,
                "revenue_miss": (res["revenue"]["label"] == "miss") if res.get("revenue") else None,
                "guide_lowered": (overall == "lowered") if overall else None,
            }
        res["fields_gap"] = gaps
        out[sym] = res
    return out


def check_valuation_inputs(pack: dict) -> list[dict]:
    """Return [{ticker, fields:[...]}] when a ticker has no usable valuation route.

    A route is usable when EITHER:
      - DCF: fcf_ttm + shares_diluted + net_debt + revenue_ttm; OR
      - comps: target metric + >=3 peers carrying the matching multiple
        (pe with eps_ttm / ev_sales with revenue_ttm / ev_ebitda with ebitda_ttm).
    Otherwise the Bot must collect more before the worker call (exit 8).
    """
    missing = []
    for sym, t in _tickers_map(pack).items():
        if not isinstance(t, dict):
            missing.append({"ticker": sym, "fields": ["<ticker data not an object>"]})
            continue
        fields = []
        quote = t.get("quote") or {}
        if not _num(quote.get("last")) and not _num(t.get("last")):
            fields.append("quote.last")
        fw = t.get("fundamentals_web") or {}
        if not isinstance(fw, dict):
            fields.append("fundamentals_web")
            fw = {}
        is_etf = str(t.get("security_type", "")).upper() == "ETF"
        if is_etf:
            issuer = fw.get("etf_issuer") or t.get("etf_issuer") or {}
            if not _num(issuer.get("nav")):
                fields.append("fundamentals_web.etf_issuer.nav")
        else:
            dcf = _has_dcf_route(fw)
            routes = _comp_routes(fw)
            if not dcf and not routes:
                fcfv = fw.get("fcf_ttm")
                if not _num(fcfv):
                    fields.append("fundamentals_web.fcf_ttm(DCF)")
                elif fcfv <= 0:
                    fields.append("fundamentals_web.fcf_ttm(DCF, <=0)")
                if not _num(fw.get("shares_diluted")) or fw.get("shares_diluted", 0) <= 0:
                    fields.append("fundamentals_web.shares_diluted")
                if not _num(fw.get("net_debt")):
                    fields.append("fundamentals_web.net_debt")
                if not _num(fw.get("revenue_ttm")):
                    fields.append("fundamentals_web.revenue_ttm")
                peers = fw.get("peers")
                if not isinstance(peers, list) or len(peers) < 3:
                    fields.append("fundamentals_web.peers(>=3)")
                else:
                    fields.append("fundamentals_web.peers.multiples(3+ per lens, matching eps/revenue/ebitda)")
        if fields:
            missing.append({"ticker": sym, "fields": fields})
    return missing

# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
def request_body(system: str, job: dict, mode: str, thinking: str) -> dict:
    body: dict = {
        "model": os.environ.get("DEEPSEEK_MODEL", MODEL[mode]).strip(),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": ANCHOR},
            {"role": "user", "content": compact(job_payload(job))},
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": MAX_TOKENS[mode],
        "stream": False,
    }
    if thinking == "on":
        body["thinking"] = {"type": "enabled"}
        body["reasoning_effort"] = "high"
    else:
        # DeepSeek defaults to thinking ON; structured routine work must disable it
        # explicitly or reasoning tokens are billed as output.
        body["thinking"] = {"type": "disabled"}
        body["temperature"] = 0.2
    return body


def http_call(key: str, body: dict, timeout: int) -> tuple[dict, int]:
    base = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    req = urllib.request.Request(
        base + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8")), 200
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:600]
        print(f"HTTP {exc.code}: {detail}", file=sys.stderr)
        return {}, exc.code
    except urllib.error.URLError as exc:
        if "timed out" in str(exc.reason).lower():
            print("timeout", file=sys.stderr)
            return {}, -1
        print(f"network error: {exc.reason}", file=sys.stderr)
        return {}, -2


def extract(payload: dict) -> tuple[str, str, dict]:
    choice = (payload.get("choices") or [{}])[0]
    content = (choice.get("message") or {}).get("content") or ""
    finish = str(choice.get("finish_reason") or "")
    usage = payload.get("usage") or {}
    usage["request_id"] = payload.get("id", "")
    return content, finish, usage


def parse_json(content: str) -> dict:
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no JSON object in model output")
    return json.loads(text[start:end + 1])


def validate(obj: object) -> list[str]:
    errs: list[str] = []
    if not isinstance(obj, dict):
        return ["output is not a JSON object"]
    if obj.get("status") not in {"ok", "partial", "blocked"}:
        errs.append("missing/invalid status")
    tickers = obj.get("tickers")
    if not isinstance(tickers, list):
        return errs + ["tickers must be a list"]
    for t in tickers:
        if not isinstance(t, dict):
            errs.append("ticker entry is not an object")
            continue
        sym = t.get("symbol") or "?"
        if "stance" in t:
            errs.append(f"{sym}: worker must not emit stance")
        if not isinstance(t.get("confidence_block"), dict):
            errs.append(f"{sym}: missing confidence_block")
        if not isinstance(t.get("challenge_nodes"), list):
            errs.append(f"{sym}: missing challenge_nodes")
    return errs


# ---------------------------------------------------------------------------
# main path
# ---------------------------------------------------------------------------
def _clean_optional_list(items: list) -> tuple[list, int]:
    kept = []
    for item in items:
        low = str(item).lower()
        if "wacc" in low or low.startswith("social_x"):
            continue
        kept.append(item)
    return kept, len(items) - len(kept)


def clean_optional(result: dict) -> None:
    """Recursively drop optional gaps/limiting noise (social_x / WACC), incl. nested
    valuation.fields_gap. Works for every routine, not only holdings."""
    removed = 0

    def walk(node) -> None:
        nonlocal removed
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {"fields_gap", "limiting"} and isinstance(value, list):
                    kept, n = _clean_optional_list(value)
                    if n:
                        node[key] = kept
                        removed += n
                elif isinstance(value, (dict, list)):
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                if isinstance(item, (dict, list)):
                    walk(item)

    walk(result)
    if removed:
        result.setdefault("warnings", []).append(f"cleaned optional gaps/limiting: {removed} item(s)")


def _safe_job_id(job: dict) -> str:
    raw = str(job.get("job_id") or "job")
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", raw)[:80]
    return safe or "job"


def _job_routine(job: dict) -> str:
    """Resolve the routine name for raw filenames.

    Priority: explicit job.routine -> pack.routine -> derive from job_id
    (e.g. 20261029-holdings-0826 -> holdings). Never fall back to mode.
    """
    payload = job_payload(job)
    for source in (job, payload):
        value = source.get("routine") if isinstance(source, dict) else None
        if isinstance(value, str) and value.strip():
            return re.sub(r"[^A-Za-z0-9_.-]", "_", value.strip())[:40]
    job_id = str(job.get("job_id") or "")
    parts = job_id.split("-")
    if len(parts) >= 3 and parts[0].isdigit() and len(parts[0]) == 8:
        middle = ""
        if len(parts) >= 3 and parts[-1].isdigit() and len(parts[-1]) == 4:
            middle = "-".join(parts[1:-1])          # YYYYMMDD-<routine>-HHMM
        elif len(parts) >= 4 and parts[1].isdigit() and len(parts[1]) == 4:
            middle = "-".join(parts[2:])            # YYYYMMDD-HHMM-<routine> (tolerated)
        middle = middle.strip()
        if middle:
            return re.sub(r"[^A-Za-z0-9_.-]", "_", middle)[:40]
    return "routine"


def write_raw(job: dict, payload: dict, exit_code: int) -> None:
    """Write a per-run raw copy atomically under out/raw/.

    Filenames use the *actual* local start time of this script (never the planned
    schedule time or a stale job_id), and a `.worker.` infix so a routine's own
    stdout redirect (if any) can never collide with these files.
    """
    try:
        raw_dir = OUT_DEFAULT / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now().astimezone()
        stamp = now.strftime("%Y%m%d-%H%M%S") + f"-{now.microsecond // 1000:03d}-{uuid.uuid4().hex[:6]}"
        routine = _job_routine(job)
        base = f"{stamp}-{routine}-{_safe_job_id(job)}"
        payload_path = raw_dir / f"{base}.worker.stdout.json"
        tmp = raw_dir / f".{base}.worker.stdout.json.tmp"
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        tmp.write_text(text, encoding="utf-8")
        # verify the file is valid JSON before publishing it
        json.loads(tmp.read_text(encoding="utf-8"))
        tmp.replace(payload_path)
        (raw_dir / f"{base}.worker.exit").write_text(f"{exit_code}\n", encoding="utf-8")
        (raw_dir / f"{base}.worker.meta.json").write_text(json.dumps({
            "job_id": job.get("job_id", ""),
            "routine": _job_routine(job),
            "exit_code": exit_code,
            "written_at": now.isoformat(),
            "job_asof": job.get("asof", ""),
            "stdout_file": payload_path.name,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:  # never fail the run
        print(f"raw log skipped: {exc}", file=sys.stderr)


def run_analysis(job: dict, key: str) -> int:
    mode = job_mode(job)
    pack = job_payload(job)
    missing = check_valuation_inputs(pack)
    if missing and not job.get("allow_incomplete"):
        payload8 = {
            "schema": "master.deepseek.jobcheck/v1",
            "status": "incomplete",
            "message": "valuation inputs missing: fix the job (Web collect) and rerun; "
                       "set allow_incomplete=true only after retry budget is spent",
            "missing": missing,
        }
        sys.stdout.write(json.dumps(payload8, ensure_ascii=False) + "\n")
        write_raw(job, payload8, 8)
        print("jobcheck: incomplete -> exit 8 (no API call)", file=sys.stderr)
        return 8
    thinking = os.environ.get("DEEPSEEK_THINKING") or ("off" if mode == "routine" else "on")
    eflags = earnings_flags(pack)
    system, system_sha = build_system(mode, set(eflags.values()))
    timeout = int(os.environ.get("DEEPSEEK_TIMEOUT", "240"))

    body = request_body(system, job, mode, thinking)
    started = time.time()
    payload, code = http_call(key, body, timeout)
    if code == -1:
        return 7
    if code == -2:
        return 3
    if code in (401, 402, 403):
        return 2
    if code in (429, 500, 502, 503, 504):
        for backoff in (2, 4, 8):
            time.sleep(backoff + random.random())
            payload, code = http_call(key, body, timeout)
            if code == 200:
                break
        if code != 200:
            return 6

    content, finish, usage = extract(payload)
    if not content.strip() or finish == "length":
        # retry once with thinking disabled, lower temperature, larger budget
        body = request_body(system, job, mode, "off")
        body["temperature"] = 0.1
        body["max_tokens"] = int(MAX_TOKENS[mode] * 1.5)
        payload, code = http_call(key, body, timeout)
        if code == 200:
            content, finish, usage = extract(payload)

    def _try_parse(text: str, finish_reason: str):
        if not text.strip() or finish_reason == "length":
            return None
        try:
            obj = parse_json(text)
        except (ValueError, json.JSONDecodeError):
            return None
        if not isinstance(obj, dict):
            return None
        normalized = []
        for t in obj.get("tickers", []):
            if not isinstance(t, dict):
                continue
            if "symbol" not in t and t.get("ticker"):
                t["symbol"] = t["ticker"]
                normalized.append(str(t["symbol"]))
            t.pop("ticker", None)
        clean_optional(obj)
        if normalized:
            obj.setdefault("warnings", []).append(
                f"normalized ticker->symbol for {', '.join(normalized)}")
        if validate(obj):
            return None
        return obj

    result = _try_parse(content, finish)
    repair = 0
    while result is None and repair < 2:
        repair += 1
        print(f"worker: invalid JSON/schema -> repair attempt {repair}", file=sys.stderr)
        body = request_body(system, job, mode, "off")
        body["temperature"] = 0.1
        body["max_tokens"] = int(MAX_TOKENS[mode] * 1.5)
        body["messages"].append({
            "role": "user",
            "content": "Your previous answer was not valid JSON or did not match the schema. "
                       "Return ONLY one valid JSON object matching the schema. No markdown, no prose.",
        })
        payload, code = http_call(key, body, timeout)
        if code == -1:
            return 7
        if code == -2:
            return 3
        if code != 200:
            write_raw(job, {"schema": "master.deepseek.invalid/v1",
                            "error": f"http {code}", "repair_attempt": repair}, 4)
            return 4
        content, finish, usage = extract(payload)
        result = _try_parse(content, finish)
    if result is None:
        truncated = finish == "length"
        write_raw(job, {
            "schema": "master.deepseek.invalid/v1",
            "error": "truncated" if truncated else "invalid_json_or_schema",
            "finish_reason": finish,
            "content_tail": content[:3000],
        }, 5 if truncated else 4)
        return 5 if truncated else 4

    computed = compute_comps(pack)
    computed_e = compute_earnings(pack)
    for t in result.get("tickers", []):
        sym = t.get("symbol")
        if sym in computed:
            t["computed_comps"] = computed[sym]
        if sym in computed_e:
            t["computed_earnings"] = computed_e[sym]
            if not isinstance(t.get("earnings"), dict):
                result.setdefault("warnings", []).append(
                    f"{sym}: earnings window flagged but worker returned no earnings block")
        elif "earnings" in t:
            t.pop("earnings", None)   # not flagged -> do not surface model-only earnings

    used_thinking = "disabled" if isinstance(body.get("thinking"), dict) and \
        body["thinking"].get("type") == "disabled" else "enabled"
    result.update({
        "schema": "master.deepseek.result/v1",
        "job_id": job.get("job_id", ""),
        "mode": mode,
        "model": body["model"],
        "thinking": used_thinking,
        "request_id": usage.get("request_id", ""),
        "system_sha256": system_sha,
        "earnings_phases": sorted(set(eflags.values())),
        "prompt_sha256": sha256(compact(job_payload(job))),
        "cache": {
            "hit": usage.get("prompt_cache_hit_tokens", 0),
            "miss": usage.get("prompt_cache_miss_tokens", 0),
        },
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        },
        "latency_ms": int((time.time() - started) * 1000),
        "result_path": str(OUT_DEFAULT / "current.result.json"),
        "analysis_source": "deepseek",
    })

    OUT_DEFAULT.mkdir(parents=True, exist_ok=True)
    result_file = OUT_DEFAULT / "current.result.json"
    result_file.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for f in (OUT_DEFAULT / "current.result.json",):
        try:
            f.chmod(0o600)
        except OSError:
            pass
    memo = result.get("memo")
    if isinstance(memo, str) and memo.strip():
        memo_file = OUT_DEFAULT / "current.memo.md"
        memo_file.write_text(memo, encoding="utf-8")
        try:
            memo_file.chmod(0o600)
        except OSError:
            pass

    out = {
        "schema": "master.deepseek.result/v1",
        "job_id": result["job_id"],
        "status": result.get("status"),
        "analysis_source": "deepseek",
        "model": result["model"],
        "thinking": result["thinking"],
        "asof": job.get("asof") or "",
        "tickers": [
            {
                "symbol": t.get("symbol"),
                "thesis": t.get("thesis", ""),
                "conviction": t.get("conviction"),
                "confidence_block": t.get("confidence_block"),
                "challenge_nodes": t.get("challenge_nodes"),
                "valuation": t.get("valuation"),
                "trap": t.get("trap"),
                "priced_in": t.get("priced_in"),
                "invalidation_candidates": t.get("invalidation_candidates", []),
                "key_risks": t.get("key_risks", []),
                "fields_gap": t.get("fields_gap", []),
                "computed_comps": t.get("computed_comps"),
                **({"earnings": t.get("earnings"),
                    "computed_earnings": t.get("computed_earnings")}
                   if "computed_earnings" in t else {}),
            }
            for t in result.get("tickers", [])
        ],
        "errors": result.get("errors", []),
        "warnings": result.get("warnings", []),
        "usage": result["usage"],
        "cache": result["cache"],
        "result_path": result["result_path"],
    }
    write_raw(job, out, 0)
    sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    print(f"worker: mode={mode} model={result['model']} thinking={result['thinking']} "
          f"latency_ms={result['latency_ms']} usage={json.dumps(result['usage'])}", file=sys.stderr)
    return 0


def selftest(ping: bool) -> int:
    key = read_key()
    report = {
        "schema": "master.deepseek.selftest/v1",
        "workspace": str(WORKSPACE),
        "key_present": bool(key),
        "key_source": "file" if SECRET_DEFAULT.is_file() else ("env" if key else "none"),
        "job_file": os.environ.get("MASTER_JOB", str(JOB_DEFAULT)),
        "system_chars": {},
        "files_ok": True,
        "ping": "skipped",
    }
    try:
        report["system_chars"]["routine"] = len(build_system("routine")[0])
        report["system_chars"]["deep"] = len(build_system("deep")[0])
        report["system_chars"]["routine+earnings"] = len(
            build_system("routine", EARNINGS_PHASES)[0])
    except FileNotFoundError as exc:
        report["files_ok"] = False
        report["error"] = str(exc)
    if ping and key:
        body = {
            "model": os.environ.get("DEEPSEEK_MODEL", MODEL["routine"]),
            "messages": [
                {"role": "system", "content": "Return only valid json. Example: {\"status\":\"ok\",\"tickers\":[]}"},
                {"role": "user", "content": "{\"ping\":true}"},
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 16,
            "thinking": {"type": "disabled"},
        }
        payload, code = http_call(key, body, 30)
        report["ping"] = "ok" if code == 200 else f"failed(http {code})"
        if code == 200:
            report["usage"] = extract(payload)[2]
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["key_present"] and report["files_ok"] else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", help="job JSON file (default: <workspace>/jobs/current.json)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--ping", action="store_true", help="with --selftest: tiny real request")
    ap.add_argument("--dump-system", action="store_true")
    ap.add_argument("--check-job", action="store_true",
                    help="only validate valuation inputs of the job (exit 8 if incomplete)")
    args = ap.parse_args()

    if args.check_job:
        try:
            job = load_job(args.pack)
        except (FileNotFoundError, ValueError) as exc:
            print(f"job error: {exc}", file=sys.stderr)
            return 2
        missing = check_valuation_inputs(job_payload(job))
        print(json.dumps({"schema": "master.deepseek.jobcheck/v1",
                          "status": "incomplete" if missing else "ok",
                          "missing": missing}, ensure_ascii=False, indent=2))
        return 8 if missing else 0

    if args.selftest:
        return selftest(args.ping)
    if args.dump_system:
        for mode in ("routine", "deep"):
            system, digest = build_system(mode)
            print(f"{mode}: chars={len(system)} sha256={digest}", file=sys.stderr)
        for ph in EARNINGS_PHASES:
            system, digest = build_system("routine", [ph])
            print(f"routine+{ph}: chars={len(system)} sha256={digest}", file=sys.stderr)
        return 0

    try:
        job = load_job(args.pack)
    except (FileNotFoundError, ValueError) as exc:
        print(f"job error: {exc}", file=sys.stderr)
        return 2
    key = read_key()
    if not key:
        print("no DeepSeek key (file .secrets/deepseek.key or DEEPSEEK_API_KEY)", file=sys.stderr)
        return 2
    return run_analysis(job, key)


if __name__ == "__main__":
    sys.exit(main())
