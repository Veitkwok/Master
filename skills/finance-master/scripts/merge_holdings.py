#!/usr/bin/env python3
"""Merge live (IBKR/Schwab) positions with manual broker lots (e.g. HSBC).

Deterministic book-building for the holdings review. No orders, no watchlist
writes, no network I/O. Market prices must be supplied by the caller and must
come from this round's IBKR quotes — this script never invents a price.

    python3 merge_holdings.py \\
        --manual /workspace/master/state/manual_holdings.json \\
        --live live.json \\
        --prices prices.json \\
        --asof 2026-11-11
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

SCHEMA = "master.manual_holdings/v1"
STALE_DAYS = 30
LIVE_BROKERS = ("IBKR", "Schwab")
LIVE_KEYS = {"ibkr": "IBKR", "schwab": "Schwab"}
# Reserved names: live connectors must not also appear in the manual file
# (would double-count). Matching is case-insensitive.
LIVE_BROKER_ALIASES = {
    "ibkr": "IBKR",
    "interactive brokers": "IBKR",
    "interactive brokers (ibkr)": "IBKR",
    "schwab": "Schwab",
    "charles schwab": "Schwab",
    "嘉信": "Schwab",
}

TWOPLACES = Decimal("0.01")
SIXPLACES = Decimal("0.000001")


class HoldingsError(ValueError):
    pass


def D(x: Any) -> Decimal:
    if isinstance(x, Decimal):
        return x
    if isinstance(x, bool) or x is None:
        raise HoldingsError(f"not a number: {x!r}")
    return Decimal(str(x))


def money(x: Decimal) -> float:
    return float(x.quantize(TWOPLACES, rounding=ROUND_HALF_UP))


def qty_str(q: Decimal) -> str:
    if q == q.to_integral_value():
        return str(int(q))
    return format(q.normalize(), "f")


def parse_date(value: str, field: str = "as_of") -> date:
    if not isinstance(value, str) or not value.strip():
        raise HoldingsError(f"{field} must be YYYY-MM-DD")
    text = value.strip()
    try:
        if "T" in text:
            return datetime.fromisoformat(text).date()
        return date.fromisoformat(text[:10])
    except ValueError as exc:
        raise HoldingsError(f"{field} must be YYYY-MM-DD, got {value!r}") from exc


def canon_live_broker(name: str) -> str | None:
    return LIVE_BROKER_ALIASES.get(name.strip().lower())


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except json.JSONDecodeError as exc:
        raise HoldingsError(f"invalid JSON in {path}: {exc}") from exc


def lot_from_raw(raw: dict, *, source_default: str, require_as_of: bool) -> dict:
    if not isinstance(raw, dict):
        raise HoldingsError("position must be an object")
    symbol = str(raw.get("symbol") or "").strip().upper()
    if not symbol or not symbol.replace("-", "").replace(".", "").isalnum():
        raise HoldingsError(f"invalid symbol: {raw.get('symbol')!r}")
    if "qty" in raw and raw.get("shares") is not None and raw.get("qty") is not None:
        if D(raw["qty"]) != D(raw["shares"]):
            raise HoldingsError(f"{symbol}: qty and shares disagree")
    qty_raw = raw.get("shares", raw.get("qty"))
    qty = D(qty_raw)
    if qty <= 0:
        raise HoldingsError(f"{symbol}: shares must be positive, got {qty_raw!r}")
    if raw.get("cost_basis") is not None:
        basis = D(raw["cost_basis"])
        if basis <= 0:
            raise HoldingsError(f"{symbol}: cost_basis must be positive")
        avg = basis / qty
        if raw.get("avg_cost") is not None and abs(D(raw["avg_cost"]) - avg) > Decimal("0.0001"):
            raise HoldingsError(f"{symbol}: avg_cost and cost_basis/shares disagree")
    else:
        if raw.get("avg_cost") is None:
            raise HoldingsError(f"{symbol}: avg_cost or cost_basis required")
        avg = D(raw["avg_cost"])
        if avg <= 0:
            raise HoldingsError(f"{symbol}: avg_cost must be positive")
        basis = avg * qty
    as_of = None
    if raw.get("as_of") or raw.get("asof"):
        as_of = parse_date(str(raw.get("as_of") or raw.get("asof")))
    elif require_as_of:
        raise HoldingsError(f"{symbol}: as_of required for manual lots")
    currency = str(raw.get("currency") or "USD").strip().upper() or "USD"
    source = str(raw.get("source") or source_default).strip()
    return {
        "symbol": symbol,
        "qty": qty,
        "avg_cost": avg,
        "cost_basis": basis,
        "currency": currency,
        "as_of": as_of,
        "source": source,
    }


def load_manual(path: Path | None) -> tuple[list[dict], list[str]]:
    """Return (lots, notices). Missing file → empty book, no error."""
    if path is None:
        return [], []
    if not path.is_file():
        return [], [f"manual_holdings.file_missing: {path}（本轮按无手工仓处理）"]
    data = load_json(path)
    if not isinstance(data, dict):
        raise HoldingsError("manual holdings file must be a JSON object")
    positions = data.get("positions")
    if positions is None:
        raise HoldingsError("manual holdings file missing positions[]")
    if not isinstance(positions, list):
        raise HoldingsError("positions must be a list")
    lots: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for raw in positions:
        if not isinstance(raw, dict):
            raise HoldingsError("manual position must be an object")
        broker_raw = str(raw.get("broker") or "").strip()
        if not broker_raw:
            raise HoldingsError("manual position missing broker")
        live = canon_live_broker(broker_raw)
        if live:
            raise HoldingsError(
                f"manual file must not contain live broker {broker_raw!r} "
                f"(would double-count {live})"
            )
        broker = broker_raw
        lot = lot_from_raw(raw, source_default="", require_as_of=True)
        if not lot["source"]:
            raise HoldingsError(f"{lot['symbol']}: source required for manual lots")
        key = (broker.casefold(), lot["symbol"])
        if key in seen:
            raise HoldingsError(f"duplicate manual lot: {broker} {lot['symbol']}")
        seen.add(key)
        lot["broker"] = broker
        lot["origin"] = "manual"
        lots.append(lot)
    return lots, []


def load_live(data: dict | None) -> list[dict]:
    if not data:
        return []
    if not isinstance(data, dict):
        raise HoldingsError("live book must be a JSON object")
    lots: list[dict] = []
    for key, broker in LIVE_KEYS.items():
        rows = data.get(key)
        if rows is None:
            continue
        if not isinstance(rows, list):
            raise HoldingsError(f"live.{key} must be a list")
        for raw in rows:
            lot = lot_from_raw(raw, source_default="live", require_as_of=False)
            lot["broker"] = broker
            lot["origin"] = "live"
            lots.append(lot)
    return lots


def load_prices(data: dict | None) -> dict[str, dict]:
    if not data:
        return {}
    if not isinstance(data, dict):
        raise HoldingsError("prices must be a JSON object")
    out: dict[str, dict] = {}
    for sym, row in data.items():
        symbol = str(sym).strip().upper()
        if isinstance(row, dict):
            if row.get("last") is None:
                continue
            last = D(row["last"])
            if last <= 0:
                raise HoldingsError(f"{symbol}: price last must be positive")
            out[symbol] = {
                "last": last,
                "asof": row.get("asof") or row.get("as_of") or row.get("price_asof"),
            }
        else:
            last = D(row)
            if last <= 0:
                raise HoldingsError(f"{symbol}: price last must be positive")
            out[symbol] = {"last": last, "asof": None}
    return out


def context_of(brokers: list[str]) -> str:
    names = set(brokers)
    if not names:
        return "neither"
    if names == {"IBKR"}:
        return "ibkr"
    if names == {"Schwab"}:
        return "schwab"
    if names == {"IBKR", "Schwab"}:
        return "both"
    if len(names) == 1:
        only = next(iter(names))
        if only.upper() == "HSBC" or only == "汇丰":
            return "hsbc"
        return "manual"
    return "multi"


def broker_order(names: list[str]) -> list[str]:
    seen: list[str] = []
    for preferred in LIVE_BROKERS:
        if preferred in names and preferred not in seen:
            seen.append(preferred)
    for name in names:
        if name not in seen:
            seen.append(name)
    return seen


def stale_days_between(as_of: date, run_on: date) -> int:
    return (run_on - as_of).days


def merge_book(
    live_lots: list[dict],
    manual_lots: list[dict],
    prices: dict[str, dict],
    run_on: date,
    stale_after: int = STALE_DAYS,
    themes: dict[str, str] | None = None,
) -> dict:
    lots = list(live_lots) + list(manual_lots)
    by_symbol: OrderedDict[str, list[dict]] = OrderedDict()
    for lot in lots:
        by_symbol.setdefault(lot["symbol"], []).append(lot)

    gaps: list[str] = []
    positions: list[dict] = []
    for symbol, symbol_lots in by_symbol.items():
        total_qty = sum((lot["qty"] for lot in symbol_lots), Decimal("0"))
        total_basis = sum((lot["cost_basis"] for lot in symbol_lots), Decimal("0"))
        avg = total_basis / total_qty if total_qty else Decimal("0")
        brokers_out = []
        any_manual = False
        oldest_manual: date | None = None
        for lot in symbol_lots:
            rec = {
                "broker": lot["broker"],
                "qty": _qty_out(lot["qty"]),
                "avg_cost": _avg_out(lot["avg_cost"]),
                "source": lot["origin"],
            }
            if lot["origin"] == "manual":
                any_manual = True
                rec["as_of"] = lot["as_of"].isoformat() if lot["as_of"] else None
                rec["source"] = lot["source"] or "manual"
                rec["origin"] = "manual"
                days = stale_days_between(lot["as_of"], run_on) if lot["as_of"] else None
                rec["stale"] = bool(days is not None and days > stale_after)
                if rec["stale"]:
                    gaps.append(
                        f"manual_holdings.stale: {symbol} {lot['broker']} as_of "
                        f"{rec['as_of']}（已超过 {stale_after} 天，请向用户确认是否仍持有）"
                    )
                if lot["as_of"] and (oldest_manual is None or lot["as_of"] < oldest_manual):
                    oldest_manual = lot["as_of"]
            else:
                rec["origin"] = "live"
            brokers_out.append(rec)
        ordered_names = broker_order([b["broker"] for b in brokers_out])
        brokers_sorted = sorted(
            brokers_out, key=lambda b: ordered_names.index(b["broker"])
        )
        parts = [f"{b['broker']} {qty_str(D(b['qty']))}" for b in brokers_sorted]
        breakdown = f"{symbol} {qty_str(total_qty)}（{'+'.join(parts)}）"
        quote = prices.get(symbol)
        last = quote["last"] if quote else None
        price_asof = quote["asof"] if quote else None
        market_value = (total_qty * last) if last is not None else None
        unrealized_pct = None
        if last is not None and avg > 0:
            unrealized_pct = (last - avg) / avg * Decimal("100")
        if last is None:
            gaps.append(
                f"manual_holdings.missing_price: {symbol} 无本轮 IBKR 现价，"
                "市值未计入集中度（不得用网页行情顶替）"
                if any_manual else
                f"holdings.missing_price: {symbol} 无本轮 IBKR 现价，市值未计入集中度"
            )
        if any_manual:
            as_of_txt = oldest_manual.isoformat() if oldest_manual else "unknown"
            manual_brokers = [
                b["broker"] for b in brokers_sorted if b.get("origin") == "manual"
            ]
            uniq: list[str] = []
            for n in manual_brokers:
                if n not in uniq:
                    uniq.append(n)
            label = "、".join(uniq)
            note = f"{label} 数量为手工录入（as_of {as_of_txt}，有过期风险）"
        else:
            note = None
        positions.append({
            "symbol": symbol,
            "qty": _qty_out(total_qty),
            "avg_cost": _avg_out(avg),
            "last": money(last) if last is not None else None,
            "market_value": money(market_value) if market_value is not None else None,
            "unrealized_pct": float(unrealized_pct.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
            if unrealized_pct is not None else None,
            "price_asof": price_asof,
            "context": context_of([b["broker"] for b in brokers_sorted]),
            "brokers": brokers_sorted,
            "breakdown": breakdown,
            "manual_note": note,
        })

    valued = [p for p in positions if p["market_value"] is not None]
    total_mv = sum((D(p["market_value"]) for p in valued), Decimal("0"))
    for p in positions:
        if p["market_value"] is not None and total_mv > 0:
            p["weight_pct"] = float(
                (D(p["market_value"]) / total_mv * 100).quantize(
                    Decimal("0.1"), rounding=ROUND_HALF_UP
                )
            )
        else:
            p["weight_pct"] = None
    ranked = sorted(valued, key=lambda p: D(p["market_value"]), reverse=True)
    top2 = ranked[:2]
    top2_mv = sum((D(p["market_value"]) for p in top2), Decimal("0"))
    top2_pct = float((top2_mv / total_mv * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)) if total_mv and top2 else None

    theme_result = None
    if themes:
        theme_result = _theme_concentration(valued, themes, total_mv)

    # Sort positions by market value desc, nulls last, then symbol
    positions.sort(key=lambda p: (
        0 if p["market_value"] is not None else 1,
        -float(p["market_value"] or 0),
        p["symbol"],
    ))

    return {
        "schema": "master.merged_holdings/v1",
        "asof": run_on.isoformat(),
        "positions": positions,
        "totals": {
            "market_value": money(total_mv) if valued else None,
            "top2_by_value": {
                "symbols": [p["symbol"] for p in top2],
                "pct": top2_pct,
            },
            "theme": theme_result,
        },
        "gaps": gaps,
    }


def _theme_concentration(valued: list[dict], themes: dict[str, str], total_mv: Decimal) -> dict:
    groups: dict[str, list[dict]] = {}
    for p in valued:
        theme = themes.get(p["symbol"]) or themes.get(p["symbol"].upper())
        if not theme:
            continue
        groups.setdefault(theme, []).append(p)
    themes_out = []
    best_pair = None
    for theme, members in groups.items():
        members = sorted(members, key=lambda p: D(p["market_value"]), reverse=True)
        mv = sum((D(p["market_value"]) for p in members), Decimal("0"))
        pct = float((mv / total_mv * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)) if total_mv else None
        themes_out.append({
            "theme": theme,
            "symbols": [p["symbol"] for p in members],
            "pct": pct,
        })
        if len(members) >= 2 and total_mv:
            pair = members[:2]
            pair_pct = float(
                (sum((D(p["market_value"]) for p in pair), Decimal("0")) / total_mv * 100)
                .quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            )
            rec = {"theme": theme, "symbols": [p["symbol"] for p in pair], "pct": pair_pct}
            if best_pair is None or pair_pct > best_pair["pct"]:
                best_pair = rec
    themes_out.sort(key=lambda r: -(r["pct"] or 0))
    return {"groups": themes_out, "top2_same_theme": best_pair}


def _qty_out(q: Decimal) -> int | float:
    if q == q.to_integral_value():
        return int(q)
    return money(q)


def _avg_out(avg: Decimal) -> float:
    # Keep up to 6 decimal places but trim trailing zeros via float of a
    # quantized value. Prefer 3 decimals when that is exact enough for display
    # of typical equity costs (e.g. 20.428).
    q6 = avg.quantize(SIXPLACES, rounding=ROUND_HALF_UP)
    return float(q6)


def build_from_files(
    manual_path: Path | None,
    live: dict | None,
    prices: dict | None,
    run_on: date,
    stale_after: int = STALE_DAYS,
    themes: dict[str, str] | None = None,
) -> dict:
    manual_lots, notices = load_manual(manual_path)
    live_lots = load_live(live)
    book = merge_book(
        live_lots, manual_lots, load_prices(prices), run_on, stale_after, themes
    )
    if notices:
        book["gaps"] = notices + book["gaps"]
    return book


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Merge live and manual holdings (no orders).")
    ap.add_argument("--manual", type=Path, help="path to state/manual_holdings.json")
    ap.add_argument("--live", type=Path, help="JSON file with ibkr[] / schwab[] lots")
    ap.add_argument("--prices", type=Path, help="JSON file of IBKR last prices by symbol")
    ap.add_argument("--themes", type=Path, help="optional {SYM: theme} JSON")
    ap.add_argument("--asof", required=True, help="run date (YYYY-MM-DD or ISO datetime)")
    ap.add_argument("--stale-days", type=int, default=STALE_DAYS)
    args = ap.parse_args(argv)

    try:
        live = load_json(args.live) if args.live else {}
        prices = load_json(args.prices) if args.prices else {}
        themes = load_json(args.themes) if args.themes else None
        if themes is not None and not isinstance(themes, dict):
            raise HoldingsError("themes must be a JSON object")
        book = build_from_files(
            args.manual, live, prices, parse_date(args.asof, "asof"),
            args.stale_days, themes,
        )
    except HoldingsError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    json.dump(book, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
