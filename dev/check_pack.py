#!/usr/bin/env python3
"""Structural / safety checker for the Master pack.

Usage (from the Master/ repo root):

    python3 dev/check_pack.py                 # check source tree
    python3 dev/check_pack.py --installed PATH # check an installed skill dir
    python3 dev/check_pack.py --write-hash    # refresh method-core hashes
    python3 dev/check_pack.py --quiet

Exit code 0 = pass (warnings allowed), 1 = errors.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # Master/
SRC_SKILL = ROOT / "skills" / "finance-master"
HASH_FILE = ROOT / "dev" / "hash-manifest.json"

SKIP_DIRS = {"__pycache__", ".git"}
TEXT_EXT = {".md", ".yaml", ".yml", ".json", ".py", ".sh"}

REQUIRED_FILES = [
    "SKILL.md",
    "references/runbooks/kol-primary.md",
    "references/runbooks/kol-supplement.md",
    "references/runbooks/holdings-review.md",
    "references/runbooks/adhoc.md",
    "references/runtime/capabilities.md",
    "references/runtime/state.md",
    "references/runtime/approvals.md",
    "references/runtime/delivery.md",
    "references/contracts/data-pack.md",
    "references/contracts/advice-card.md",
    "references/contracts/confidence.md",
    "references/contracts/deepseek.md",
    "references/contracts/memory.md",
    "references/contracts/accounts.md",
    "references/contracts/book-and-overlaps.md",
    "references/decisions/stance.md",
    "references/decisions/target.md",
    "references/decisions/sell.md",
    "references/decisions/risk-gates.md",
    "references/engine/README.md",
    "references/engine/sherlock/GUIDE.md",
    "references/engine/sherlock/references/full-engine.md",
    "references/engine/sherlock/references/l2-confidence-contract.md",
    "references/engine/modules/company-valuation/GUIDE.md",
    "references/engine/modules/company-valuation/references/dcf.md",
    "references/engine/modules/trap-detector/GUIDE.md",
    "references/engine/modules/trap-detector/references/eight-signals.md",
    "references/engine/modules/etf/GUIDE.md",
    "references/engine/modules/x-advanced-research/GUIDE.md",
    "references/engine/docs/reference/priced-in-checklist.md",
    "scripts/deepseek_analyze.py",
]

CORE_FILES = [
    "SKILL.md",
    "references/contracts/confidence.md",
    "references/engine/sherlock/GUIDE.md",
    "references/engine/sherlock/references/full-engine.md",
    "references/engine/sherlock/references/l2-confidence-contract.md",
    "references/engine/sherlock/references/confidence-examples.md",
    "references/engine/sherlock/references/method-library/INDEX.md",
    "references/engine/modules/company-valuation/GUIDE.md",
    "references/engine/modules/company-valuation/references/dcf.md",
    "references/engine/modules/company-valuation/references/relative_valuation.md",
    "references/engine/modules/trap-detector/GUIDE.md",
    "references/engine/modules/trap-detector/references/eight-signals.md",
    "references/engine/docs/reference/priced-in-checklist.md",
]

BANNED = [
    "x_keyword_search", "x_semantic_search", "x_thread_fetch", "x_user_search",
    "search_contracts", "get_price_snapshot", "get_price_history",
    "get_account_positions", "get_account_balances", "get_account_trades",
    "get_account_orders", "create_order_instruction", "delete_order_instruction",
    "get_order_instructions", "localhost:8888", "bemix", "balder-ai",
    "koltracker", "lists/x-kol", "Grok Build", "sherlock-finance",
    "cache/_template.yaml", "DEEPSEEK_API_KEY=",
]
NEGATION = re.compile(
    r"(do not|don't|never|no |not |禁止|不得|不存在|已废|旧|skip|drop|forbidden|"
    r"this pack has no|本包无|removed|instead)",
    re.I,
)

PATH_TOKEN = re.compile(r"`([^`\n]+\.(?:md|yaml|yml|json|py|sh))`")
MAX_TOTAL = 1_500_000
MAX_FILE = 300_000
MAX_SKILL_LINES = 500


def iter_files(base: Path):
    for p in sorted(base.rglob("*")):
        if p.is_file() and not any(part in SKIP_DIRS for part in p.parts):
            yield p


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    data: dict[str, str] = {}
    key = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            data[key] = m.group(2)
        elif key and line.strip():
            data[key] = (data.get(key, "") + " " + line.strip()).strip()
    return data


def check_skill(skill: Path, errors: list[str], warnings: list[str]) -> None:
    tag = "" if skill == SRC_SKILL else f"[installed {skill}] "
    if not skill.is_dir():
        errors.append(f"{tag}skill dir missing: {skill}")
        return

    # 1) structure
    skill_mds = [p for p in iter_files(skill) if p.name == "SKILL.md"]
    if len(skill_mds) != 1 or skill_mds[0].parent != skill:
        errors.append(f"{tag}expected exactly one SKILL.md at skill root, found {[str(p) for p in skill_mds]}")
    guides = list((skill / "references" / "engine").rglob("GUIDE.md"))
    if len(guides) != 20:
        warnings.append(f"{tag}engine GUIDE.md count is {len(guides)} (expected 20)")

    # 2) required files
    for rel in REQUIRED_FILES:
        if not (skill / rel).is_file():
            errors.append(f"{tag}missing required file: {rel}")

    # 3) frontmatter
    skill_md = skill / "SKILL.md"
    if skill_md.is_file():
        text = skill_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        name = fm.get("name", "").strip()
        desc = fm.get("description", "").strip()
        if name != skill.name:
            errors.append(f"{tag}SKILL.md name '{name}' != folder '{skill.name}'")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name):
            errors.append(f"{tag}name must be lowercase-hyphen <=64 chars")
        if not desc:
            errors.append(f"{tag}description missing")
        if len(desc) > 1024:
            errors.append(f"{tag}description {len(desc)} chars > 1024")
        lines = text.count("\n") + 1
        if lines > MAX_SKILL_LINES:
            errors.append(f"{tag}SKILL.md has {lines} lines > {MAX_SKILL_LINES}")

    # 4) sizes
    total = 0
    for p in iter_files(skill):
        size = p.stat().st_size
        total += size
        if size > MAX_FILE:
            warnings.append(f"{tag}large file {p.relative_to(skill)}: {size/1024:.0f}KB")
    if total > MAX_TOTAL:
        errors.append(f"{tag}skill total {total/1024:.0f}KB > {MAX_TOTAL/1024:.0f}KB")

    # 5) path resolution + banned words
    for p in iter_files(skill):
        if p.suffix not in TEXT_EXT:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        rel = p.relative_to(skill)
        for m in PATH_TOKEN.finditer(text):
            token = m.group(1).strip()
            if any(x in token for x in ("://", "{", "}", "<", ">", "*", "…", "|", "xxx", "...",
                                        "YYYY", " ", "python", ".cache", "lib/", "cache/_template.yaml")):
                continue
            if token.startswith(("/", "state/", "out/", "packs/", "jobs/", ".secrets/", "skill/")) or "/" not in token:
                continue
            candidates = [
                skill / token,                 # skill-root path
                skill / "references" / token,  # shorthand inside references/
                p.parent / token,              # file-relative (engine docs)
                ROOT / token,                  # repo-root path (dev/ scripts in docs)
            ]
            if not any(c.exists() for c in candidates):
                bucket = warnings if "engine" in rel.parts else errors
                bucket.append(f"{tag}broken path in {rel}: `{token}`")
        for line in text.splitlines():
            for word in BANNED:
                if word in line and not NEGATION.search(line):
                    errors.append(f"{tag}banned token '{word}' in {rel}: {line.strip()[:120]}")

    # 6) safety text must exist
    advice = skill / "references/contracts/advice-card.md"
    if advice.is_file():
        t = advice.read_text(encoding="utf-8")
        for must in ("order_sent: false", "schwab_trade: forbidden", "买入", "目标价", "卖出"):
            if must not in t:
                errors.append(f"{tag}advice-card missing required text: {must}")

    # 7) hashes
    if HASH_FILE.is_file() and skill == SRC_SKILL:
        expected = json.loads(HASH_FILE.read_text(encoding="utf-8"))
        for rel, want in expected.items():
            p = skill / rel
            if not p.is_file():
                errors.append(f"{tag}core file missing: {rel}")
                continue
            got = hashlib.sha256(p.read_bytes()).hexdigest()
            if got != want:
                errors.append(f"{tag}method-core hash changed: {rel} (run --write-hash only after review)")


def write_hashes() -> int:
    hashes = {}
    for rel in CORE_FILES:
        p = SRC_SKILL / rel
        if not p.is_file():
            print(f"missing core file: {rel}", file=sys.stderr)
            return 1
        hashes[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    HASH_FILE.parent.mkdir(parents=True, exist_ok=True)
    HASH_FILE.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(hashes)} hashes -> {HASH_FILE}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--installed", metavar="PATH", help="check an installed skill dir")
    ap.add_argument("--write-hash", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.write_hash:
        return write_hashes()

    errors: list[str] = []
    warnings: list[str] = []
    check_skill(SRC_SKILL, errors, warnings)
    if args.installed:
        check_skill(Path(args.installed).expanduser(), errors, warnings)

    if not args.quiet:
        for w in warnings:
            print("WARN:", w)
        for e in errors:
            print("ERROR:", e)
        print(f"\ncheck_pack: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
