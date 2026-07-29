#!/usr/bin/env python3
"""Query the AST-derived knowledge base built by kb_build.py.

Usage:
    kb_query.py symbol <name>      # where is <name> defined (+ signature/doc)
    kb_query.py file <path>        # symbols, imports and calls of a file
    kb_query.py callers <name>     # files whose code calls <name>
    kb_query.py search <regex>     # search symbol names by regex
    kb_query.py imports <path>     # what a file imports / who imports it
    kb_query.py stale              # files out of sync with the kb
    kb_query.py stats              # kb overview

All output is JSON (one object) for easy consumption by agents.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(out)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


ROOT = repo_root()
KB = ROOT / ".agentic" / "kb"


def load_index() -> dict:
    idx = KB / "index.json"
    if not idx.exists():
        sys.exit("no knowledge base found — run kb_build.py first")
    return json.loads(idx.read_text())


def load_entry(rel: str) -> dict | None:
    p = KB / "files" / (rel + ".json")
    if p.exists():
        return json.loads(p.read_text())
    return None


def emit(obj):
    print(json.dumps(obj, indent=1))


def base_name(qualname: str) -> str:
    return qualname.rsplit(".", 1)[-1]


def cmd_symbol(index, name):
    results = []
    for rel, meta in index["files"].items():
        matches = [q for q in meta.get("symbols", [])
                   if q == name or base_name(q) == name]
        if not matches:
            continue
        entry = load_entry(rel)
        if entry is None:
            continue
        for sym in entry["symbols"]:
            if sym["qualname"] in matches:
                results.append({**sym, "path": rel})
    emit({"query": name, "definitions": results})


def cmd_file(index, path):
    rel = str(Path(path))
    entry = load_entry(rel)
    if entry is None:
        # try to resolve fuzzy path
        candidates = [r for r in index["files"] if r.endswith(rel)]
        if len(candidates) == 1:
            entry = load_entry(candidates[0])
    if entry is None:
        sys.exit(f"no kb entry for {path}")
    emit(entry)


def cmd_callers(index, name):
    callers = []
    for rel in index["files"]:
        entry = load_entry(rel)
        if entry is None:
            continue
        hits = [c for c in entry.get("calls", [])
                if c == name or c.split(".")[-1] == name or c.endswith("." + name)]
        if hits:
            callers.append({"path": rel, "calls": sorted(set(hits))})
    emit({"query": name, "callers": callers})


def cmd_search(index, pattern):
    rx = re.compile(pattern)
    hits = {q: paths for q, paths in index["symbols"].items() if rx.search(q)}
    emit({"query": pattern, "symbols": hits})


def cmd_imports(index, path):
    rel = str(Path(path))
    entry = load_entry(rel)
    imports = entry["imports"] if entry else []
    stem = Path(rel).stem
    imported_by = []
    for other, _meta in index["files"].items():
        if other == rel:
            continue
        oentry = load_entry(other)
        if oentry and any(stem in imp for imp in oentry.get("imports", [])):
            imported_by.append(other)
    emit({"path": rel, "imports": imports, "imported_by": imported_by})


def cmd_stale(index):
    stale, missing = [], []
    for rel, meta in index["files"].items():
        p = ROOT / rel
        if not p.exists():
            missing.append(rel)
        elif hashlib.sha256(p.read_bytes()).hexdigest() != meta["hash"]:
            stale.append(rel)
    emit({"stale": stale, "deleted": missing})


def cmd_stats(index):
    langs: dict[str, int] = {}
    for meta in index["files"].values():
        langs[meta["language"]] = langs.get(meta["language"], 0) + 1
    emit({
        "generated": index.get("generated"),
        "files": len(index["files"]),
        "symbols": len(index["symbols"]),
        "languages": langs,
    })


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("symbol").add_argument("name")
    sub.add_parser("file").add_argument("path")
    sub.add_parser("callers").add_argument("name")
    sub.add_parser("search").add_argument("pattern")
    sub.add_parser("imports").add_argument("path")
    sub.add_parser("stale")
    sub.add_parser("stats")
    args = ap.parse_args()

    index = load_index()
    if args.cmd == "symbol":
        cmd_symbol(index, args.name)
    elif args.cmd == "file":
        cmd_file(index, args.path)
    elif args.cmd == "callers":
        cmd_callers(index, args.name)
    elif args.cmd == "search":
        cmd_search(index, args.pattern)
    elif args.cmd == "imports":
        cmd_imports(index, args.path)
    elif args.cmd == "stale":
        cmd_stale(index)
    elif args.cmd == "stats":
        cmd_stats(index)


if __name__ == "__main__":
    main()
