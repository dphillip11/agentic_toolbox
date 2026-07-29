#!/usr/bin/env python3
"""Build the AST-derived knowledge base for a codebase.

Parses source files with tree-sitter and extracts an atomic symbol map per
file (functions, classes, methods, imports, calls), plus structural module
summaries and a global index. Output lives under .agentic/kb/.

Usage:
    kb_build.py                       # full build (respects .gitignore)
    kb_build.py --paths a.py b.ts     # rebuild specific files
    kb_build.py --since <git-ref>     # rebuild files changed since ref
    kb_build.py --check               # report stale entries, exit 1 if any

Dedicated extraction for: Python, TypeScript/JavaScript (incl. TSX/JSX),
C and C++. Other languages supported by tree-sitter-language-pack fall back
to a generic extractor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from tree_sitter_language_pack import get_parser
except ImportError:
    sys.exit(
        "tree-sitter-language-pack not installed.\n"
        "Run: pip install -r .agentic/scripts/requirements.txt"
    )

KB_VERSION = 1

LANG_BY_EXT = {
    ".py": "python",
    ".pyi": "python",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".mts": "typescript",
    ".cts": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hh": "cpp",
    # generic fallback languages
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".swift": "swift",
    ".lua": "lua",
    ".sh": "bash",
    ".bash": "bash",
}

DEDICATED = {"python", "typescript", "tsx", "javascript", "c", "cpp"}

DEFAULT_EXCLUDES = {
    ".agentic", ".git", ".github", "node_modules", "dist", "build",
    "out", "target", "vendor", "venv", ".venv", "__pycache__",
    ".next", ".svelte-kit", "coverage",
}


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(out)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def load_env(root: Path) -> dict:
    env_path = root / ".agentic" / "env.json"
    if env_path.exists():
        return json.loads(env_path.read_text())
    return {}


def list_source_files(root: Path, env: dict) -> list[Path]:
    excludes = DEFAULT_EXCLUDES | set(env.get("exclude", []))
    try:
        out = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            capture_output=True, text=True, check=True, cwd=root,
        ).stdout.splitlines()
        candidates = [root / line for line in out]
    except (subprocess.CalledProcessError, FileNotFoundError):
        candidates = [p for p in root.rglob("*") if p.is_file()]

    files = []
    for p in candidates:
        rel = p.relative_to(root)
        if any(part in excludes for part in rel.parts):
            continue
        if p.suffix.lower() in LANG_BY_EXT and p.is_file():
            files.append(p)
    return sorted(files)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def node_text(node, src: bytes) -> str:
    return src[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def find_child(node, *types):
    for child in node.children:
        if child.type in types:
            return child
    return None


def first_line(text: str) -> str:
    return text.strip().splitlines()[0].strip() if text.strip() else ""


# --------------------------------------------------------------------------
# extraction
# --------------------------------------------------------------------------

def make_symbol(kind, name, node, src, parent=None, signature="", doc=""):
    return {
        "kind": kind,
        "name": name,
        "qualname": f"{parent}.{name}" if parent else name,
        "signature": signature,
        "lines": [node.start_point[0] + 1, node.end_point[0] + 1],
        "doc": doc,
    }


def py_docstring(body_node, src) -> str:
    if body_node is None or not body_node.children:
        return ""
    stmt = body_node.children[0]
    string_node = None
    if stmt.type == "string":
        string_node = stmt
    elif stmt.type == "expression_statement" and stmt.children and stmt.children[0].type == "string":
        string_node = stmt.children[0]
    if string_node is None:
        return ""
    content = find_child(string_node, "string_content")
    raw = node_text(content, src) if content is not None else node_text(string_node, src).strip("\"' \n")
    return first_line(raw)


def extract_python(tree, src):
    symbols, imports, calls = [], [], set()

    def walk(node, parent=None):
        for child in node.children:
            t = child.type
            target = child
            if t == "decorated_definition":
                inner = find_child(child, "function_definition", "class_definition")
                if inner is not None:
                    target, t = inner, inner.type
            if t in ("function_definition", "class_definition"):
                name_node = find_child(target, "identifier")
                name = node_text(name_node, src) if name_node else "<anon>"
                params = find_child(target, "parameters")
                sig = node_text(params, src) if params else ""
                body = find_child(target, "block")
                doc = py_docstring(body, src)
                kind = "class" if t == "class_definition" else ("method" if parent else "function")
                symbols.append(make_symbol(kind, name, child, src, parent, sig, doc))
                walk(target, parent=f"{parent}.{name}" if parent else name)
            elif t in ("import_statement", "import_from_statement"):
                imports.append(first_line(node_text(child, src)))
            elif t == "call":
                fn = child.children[0] if child.children else None
                if fn is not None and fn.type in ("identifier", "attribute"):
                    calls.add(node_text(fn, src))
                walk(child, parent)
            else:
                walk(child, parent)

    walk(tree.root_node)
    return symbols, imports, sorted(calls)


def extract_js_ts(tree, src):
    symbols, imports, calls = [], [], set()

    def handle_declaration(child, parent):
        t = child.type
        if t in ("function_declaration", "generator_function_declaration"):
            name_node = find_child(child, "identifier")
            name = node_text(name_node, src) if name_node else "<anon>"
            params = find_child(child, "formal_parameters")
            sig = node_text(params, src) if params else ""
            symbols.append(make_symbol("function", name, child, src, parent, sig))
            body = find_child(child, "statement_block")
            if body is not None:
                walk(body, parent)
            return True
        if t in ("class_declaration", "abstract_class_declaration"):
            name_node = find_child(child, "type_identifier", "identifier")
            name = node_text(name_node, src) if name_node else "<anon>"
            symbols.append(make_symbol("class", name, child, src, parent))
            body = find_child(child, "class_body")
            if body is not None:
                walk(body, parent=f"{parent}.{name}" if parent else name)
            return True
        if t in ("lexical_declaration", "variable_declaration"):
            for decl in child.children:
                if decl.type != "variable_declarator":
                    continue
                name_node = find_child(decl, "identifier")
                value = find_child(decl, "arrow_function", "function_expression", "function")
                if name_node is not None and value is not None:
                    name = node_text(name_node, src)
                    params = find_child(value, "formal_parameters")
                    sig = node_text(params, src) if params else ""
                    symbols.append(make_symbol("function", name, child, src, parent, sig))
                    walk(value, parent)
                else:
                    walk(decl, parent)
            return True
        if t in ("interface_declaration", "type_alias_declaration", "enum_declaration"):
            name_node = find_child(child, "type_identifier", "identifier")
            name = node_text(name_node, src) if name_node else "<anon>"
            kind = {"interface_declaration": "interface",
                    "type_alias_declaration": "type",
                    "enum_declaration": "enum"}[t]
            symbols.append(make_symbol(kind, name, child, src, parent))
            return True
        return False

    def walk(node, parent=None):
        for child in node.children:
            t = child.type
            if handle_declaration(child, parent):
                continue
            if t == "method_definition":
                name_node = find_child(child, "property_identifier", "identifier")
                name = node_text(name_node, src) if name_node else "<anon>"
                params = find_child(child, "formal_parameters")
                sig = node_text(params, src) if params else ""
                symbols.append(make_symbol("method", name, child, src, parent, sig))
                walk(child, parent)
            elif t == "import_statement":
                imports.append(first_line(node_text(child, src)))
            elif t == "export_statement":
                inner_handled = False
                for inner in child.children:
                    if handle_declaration(inner, parent):
                        inner_handled = True
                if not inner_handled:
                    walk(child, parent)
            elif t == "call_expression":
                fn = child.children[0] if child.children else None
                if fn is not None and fn.type in ("identifier", "member_expression"):
                    calls.add(node_text(fn, src))
                walk(child, parent)
            else:
                walk(child, parent)

    walk(tree.root_node)
    return symbols, imports, sorted(calls)


def extract_c_cpp(tree, src):
    symbols, imports, calls = [], [], set()

    def declarator_name(node):
        cur = node
        while cur is not None:
            if cur.type in ("identifier", "field_identifier", "qualified_identifier",
                            "destructor_name", "operator_name"):
                return node_text(cur, src)
            nxt = None
            for child in cur.children:
                if "declarator" in child.type or child.type in (
                        "identifier", "field_identifier", "qualified_identifier",
                        "destructor_name", "operator_name"):
                    nxt = child
                    break
            cur = nxt
        return None

    def walk(node, parent=None):
        for child in node.children:
            t = child.type
            if t == "function_definition":
                decl = find_child(child, "function_declarator", "pointer_declarator",
                                  "reference_declarator")
                name = declarator_name(decl) if decl is not None else None
                sig = ""
                if decl is not None:
                    params = find_child(decl, "parameter_list")
                    if params is None:
                        fn_decl = find_child(decl, "function_declarator")
                        if fn_decl is not None:
                            params = find_child(fn_decl, "parameter_list")
                    if params is not None:
                        sig = node_text(params, src)
                symbols.append(make_symbol("function", name or "<anon>", child, src, parent, sig))
                walk(child, parent=f"{parent}.{name}" if parent and name else (name or parent))
            elif t in ("struct_specifier", "class_specifier", "enum_specifier",
                       "union_specifier"):
                name_node = find_child(child, "type_identifier")
                body = find_child(child, "field_declaration_list", "enumerator_list")
                if name_node is not None and body is not None:
                    name = node_text(name_node, src)
                    kind = t.replace("_specifier", "")
                    symbols.append(make_symbol(kind, name, child, src, parent))
                    walk(body, parent=f"{parent}.{name}" if parent else name)
                else:
                    walk(child, parent)
            elif t == "preproc_include":
                imports.append(first_line(node_text(child, src)))
            elif t == "call_expression":
                fn = child.children[0] if child.children else None
                if fn is not None and fn.type in ("identifier", "field_expression",
                                                  "qualified_identifier"):
                    calls.add(node_text(fn, src))
                walk(child, parent)
            else:
                walk(child, parent)

    walk(tree.root_node)
    return symbols, imports, sorted(calls)


GENERIC_DEF_TYPES = {
    "function_definition", "function_declaration", "method_definition",
    "method_declaration", "function_item", "class_definition",
    "class_declaration", "class_specifier", "struct_item", "enum_item",
    "trait_item", "impl_item", "interface_declaration", "type_declaration",
    "func_literal", "method", "module", "class", "singleton_method",
}

GENERIC_IMPORT_TYPES = {
    "import_declaration", "import_statement", "import_spec", "use_declaration",
    "import_header", "using_directive", "require", "preproc_include",
}


def extract_generic(tree, src):
    symbols, imports, calls = [], [], set()

    def name_of(node):
        for child in node.children:
            if child.type in ("identifier", "type_identifier", "field_identifier",
                              "name", "constant", "simple_identifier"):
                return node_text(child, src)
        return None

    def walk(node, parent=None):
        for child in node.children:
            t = child.type
            if t in GENERIC_DEF_TYPES:
                name = name_of(child) or "<anon>"
                kind = "class" if "class" in t or "struct" in t or "trait" in t else "function"
                symbols.append(make_symbol(kind, name, child, src, parent))
                walk(child, parent=f"{parent}.{name}" if parent else name)
            elif t in GENERIC_IMPORT_TYPES:
                imports.append(first_line(node_text(child, src)))
            elif "call" in t and child.children:
                fn = child.children[0]
                if "identifier" in fn.type or "expression" in fn.type:
                    calls.add(node_text(fn, src))
                walk(child, parent)
            else:
                walk(child, parent)

    walk(tree.root_node)
    return symbols, imports, sorted(calls)


EXTRACTORS = {
    "python": extract_python,
    "typescript": extract_js_ts,
    "tsx": extract_js_ts,
    "javascript": extract_js_ts,
    "c": extract_c_cpp,
    "cpp": extract_c_cpp,
}


def parse_file(path: Path, root: Path) -> dict | None:
    lang = LANG_BY_EXT.get(path.suffix.lower())
    if lang is None:
        return None
    src = path.read_bytes()
    try:
        parser = get_parser(lang)
    except Exception:
        return None
    tree = parser.parse(src)
    extractor = EXTRACTORS.get(lang, extract_generic)
    symbols, imports, calls = extractor(tree, src)
    return {
        "path": str(path.relative_to(root)),
        "language": lang,
        "hash": sha256(src),
        "loc": src.count(b"\n") + 1,
        "imports": imports,
        "symbols": symbols,
        "calls": calls,
    }


# --------------------------------------------------------------------------
# kb output
# --------------------------------------------------------------------------

def kb_dir(root: Path) -> Path:
    return root / ".agentic" / "kb"


def entry_path(root: Path, rel: str) -> Path:
    return kb_dir(root) / "files" / (rel + ".json")


def write_entry(root: Path, record: dict):
    out = entry_path(root, record["path"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=1) + "\n")


def load_index(root: Path) -> dict:
    idx = kb_dir(root) / "index.json"
    if idx.exists():
        return json.loads(idx.read_text())
    return {"version": KB_VERSION, "files": {}, "symbols": {}}


def rebuild_symbol_index(index: dict):
    symbols: dict[str, list[str]] = {}
    for rel, meta in index["files"].items():
        for name in meta.get("symbols", []):
            symbols.setdefault(name, [])
            if rel not in symbols[name]:
                symbols[name].append(rel)
    index["symbols"] = {k: sorted(v) for k, v in sorted(symbols.items())}


def write_index(root: Path, index: dict):
    index["version"] = KB_VERSION
    index["generated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rebuild_symbol_index(index)
    out = kb_dir(root) / "index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(index, indent=1) + "\n")


def write_module_summaries(root: Path, index: dict):
    """One markdown summary per source directory, listing files and symbols."""
    by_dir: dict[str, list[str]] = {}
    for rel in sorted(index["files"]):
        by_dir.setdefault(str(Path(rel).parent), []).append(rel)

    modules_dir = kb_dir(root) / "modules"
    if modules_dir.exists():
        for old in modules_dir.rglob("*.md"):
            old.unlink()

    for dirname, rels in by_dir.items():
        lines = [f"# Module: {dirname or '.'}", ""]
        for rel in rels:
            entry_file = entry_path(root, rel)
            if not entry_file.exists():
                continue
            record = json.loads(entry_file.read_text())
            lines.append(f"## {rel}  ({record['language']}, {record['loc']} loc)")
            if record["imports"]:
                lines.append(f"- imports: {len(record['imports'])}")
            for sym in record["symbols"]:
                doc = f" — {sym['doc']}" if sym.get("doc") else ""
                sig = sym.get("signature", "")
                lines.append(
                    f"- `{sym['qualname']}{sig}` [{sym['kind']}] "
                    f"L{sym['lines'][0]}-{sym['lines'][1]}{doc}"
                )
            lines.append("")
        safe = (dirname or "root").replace("/", "__")
        out = modules_dir / f"{safe}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n")


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def changed_since(root: Path, ref: str) -> list[Path]:
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMR", ref, "HEAD"],
        capture_output=True, text=True, check=True, cwd=root,
    ).stdout.splitlines()
    return [root / line for line in out if (root / line).exists()]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--paths", nargs="*", help="specific files to (re)build")
    ap.add_argument("--since", help="git ref; rebuild files changed since it")
    ap.add_argument("--check", action="store_true",
                    help="report stale/missing entries; exit 1 if any")
    args = ap.parse_args()

    root = repo_root()
    env = load_env(root)
    index = load_index(root)

    all_files = list_source_files(root, env)
    all_rels = {str(p.relative_to(root)) for p in all_files}

    if args.check:
        stale = []
        for p in all_files:
            rel = str(p.relative_to(root))
            meta = index["files"].get(rel)
            if meta is None or meta["hash"] != sha256(p.read_bytes()):
                stale.append(rel)
        removed = [rel for rel in index["files"] if rel not in all_rels]
        for rel in stale:
            print(f"stale: {rel}")
        for rel in removed:
            print(f"deleted: {rel}")
        if stale or removed:
            sys.exit(1)
        print("knowledge base is up to date")
        return

    if args.paths:
        targets = [Path(p).resolve() for p in args.paths]
        targets = [p for p in targets if p.exists()]
    elif args.since:
        targets = changed_since(root, args.since)
    else:
        targets = all_files

    targets = [p for p in targets if p.suffix.lower() in LANG_BY_EXT]

    built = 0
    for path in targets:
        record = parse_file(path, root)
        if record is None:
            continue
        write_entry(root, record)
        index["files"][record["path"]] = {
            "hash": record["hash"],
            "language": record["language"],
            "loc": record["loc"],
            "symbols": [s["qualname"] for s in record["symbols"]],
        }
        built += 1

    # prune entries for deleted files
    pruned = 0
    for rel in list(index["files"]):
        if rel not in all_rels:
            del index["files"][rel]
            stale_entry = entry_path(root, rel)
            if stale_entry.exists():
                stale_entry.unlink()
            pruned += 1

    write_index(root, index)
    write_module_summaries(root, index)
    (kb_dir(root) / "notes").mkdir(parents=True, exist_ok=True)

    print(f"kb: {built} file(s) indexed, {pruned} pruned, "
          f"{len(index['files'])} total, {len(index['symbols'])} symbols")


if __name__ == "__main__":
    main()
