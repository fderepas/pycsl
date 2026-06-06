#!/usr/bin/env python3
"""PyCSL stdlib-coverage discovery and check tool.

Walks ``src/pycsl/*.py`` (recursive) for Python AST evidence of
standard-library API usage, and reconciles the discovered set against
the three artefacts that govern stdlib coverage (see
``StdlibCoverage_Workplan.md`` and
``config/skills/pycsl-stdlib-coverage/SKILL.md``):

  1. ``calls-english.md``                       — English semantics per entry
  2. ``calls-pycsl.md``                         — PyCSL contract per entry
  3. ``src/pycsl_lib/``                         — generated stub files

Modes:

  ``stdlib-coverage.py --discover``    write canonical report to
                                       ``stdlib-coverage-report.toml``

  ``stdlib-coverage.py --check K``     compare report against artefacts;
                                       ``K`` ∈ ``english`` | ``pycsl`` |
                                       ``stubs`` | ``all``. Exits 1 on drift.

  ``stdlib-coverage.py --diff [base]`` diff report vs a baseline TOML
                                       (default: ``stdlib-coverage-report.toml``
                                       at HEAD).

Workplan PR 1 — see ``.claude/plans/stdlib-coverage-plan.md`` §"PR 1".

Exit codes (workplan §13 step 7):

  0  pass
  1  drift detected (missing entry, contract change, dead stub, ...)
  2  tool error (unreadable file, malformed TOML, ...)
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Paths — ``src/pycsl_lib/`` is the post-rename location (was
# ``data/lib_stubs/`` until StdlibCoverage workplan PR 3).
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PYCSL_ROOT = REPO_ROOT / "src" / "pycsl"
REPORT_PATH = REPO_ROOT / "stdlib-coverage-report.toml"
CALLS_ENGLISH = REPO_ROOT / "calls-english.md"
CALLS_PYCSL = REPO_ROOT / "calls-pycsl.md"


def stub_dirs() -> List[Path]:
    """Return the canonical stub directory."""
    return [REPO_ROOT / "src" / "pycsl_lib"]


# ---------------------------------------------------------------------------
# Builtins and stdlib top-level modules.
# ---------------------------------------------------------------------------
# We pick up imports that name any of these as a top-level module. The
# exact line between "stdlib" and "user code" is fuzzy at the edges
# (e.g. ``typing_extensions``); a conservative set is fine. Anything
# beyond this is reported as a non-stdlib import and skipped.

_STDLIB_TOP_LEVEL: Set[str] = {
    # Frequently-used; not exhaustive, but covers what src/pycsl/ uses.
    "abc", "argparse", "ast", "atexit", "base64", "bisect", "builtins",
    "calendar", "cmath", "cmd", "codecs", "collections", "concurrent",
    "configparser", "contextlib", "copy", "copyreg", "csv", "ctypes",
    "dataclasses", "datetime", "decimal", "difflib", "enum", "errno",
    "filecmp", "fileinput", "fnmatch", "fractions", "functools", "gc",
    "getopt", "getpass", "glob", "graphlib", "hashlib", "heapq", "html",
    "http", "importlib", "inspect", "io", "ipaddress", "itertools", "json",
    "logging", "math", "mimetypes", "numbers", "operator", "os", "pathlib",
    "pickle", "pkgutil", "platform", "posixpath", "pprint", "queue",
    "random", "re", "secrets", "select", "shlex", "shutil", "signal",
    "socket", "sqlite3", "ssl", "stat", "statistics", "string", "struct",
    "subprocess", "sys", "tempfile", "textwrap", "threading", "time",
    "timeit", "tokenize", "tomllib", "traceback", "types", "typing",
    "unicodedata", "unittest", "urllib", "uuid", "warnings", "weakref",
    "xml", "xmlrpc", "zipfile", "zoneinfo",
    # Builtins module — `import builtins` and ``builtins.<name>``.
    # The bare builtins (``len``, ``range``, ``isinstance``) are tracked
    # separately under ``builtins.*`` regardless of an explicit import.
}

_BUILTINS: Set[str] = {
    "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes",
    "callable", "chr", "classmethod", "compile", "complex", "delattr",
    "dict", "dir", "divmod", "enumerate", "eval", "exec", "filter",
    "float", "format", "frozenset", "getattr", "globals", "hasattr",
    "hash", "help", "hex", "id", "input", "int", "isinstance",
    "issubclass", "iter", "len", "list", "locals", "map", "max",
    "memoryview", "min", "next", "object", "oct", "open", "ord", "pow",
    "print", "property", "range", "repr", "reversed", "round", "set",
    "setattr", "slice", "sorted", "staticmethod", "str", "sum", "super",
    "tuple", "type", "vars", "zip",
}


# ---------------------------------------------------------------------------
# Entry record
# ---------------------------------------------------------------------------
# Each discovered usage produces an Entry with:
#   ``name``    canonical dotted path (``os.path.join``, ``re.compile``,
#               ``builtins.len``, ``str.split``).
#   ``kind``    one of ``module_function``, ``builtin``, ``method``,
#               ``class``, ``constant``.
#   ``call_level``   True iff invoked at least once (workplan §2.2 case 2).
#   ``type_level``   True iff referenced in a function annotation
#                    (workplan §2.2 case 1).
#   ``locations``    list of "<file>:<line>" strings where the symbol
#                    occurs. Sorted, de-duplicated.


def _new_entry(name: str, kind: str) -> Dict[str, Any]:
    return {
        "name": name,
        "kind": kind,
        "call_level": False,
        "type_level": False,
        "locations": set(),
    }


# ---------------------------------------------------------------------------
# AST walker
# ---------------------------------------------------------------------------

class _StdlibVisitor(ast.NodeVisitor):
    """Per-file walker. Populates ``entries`` (the shared dict the caller
    owns) with discovered API references."""

    def __init__(self, filepath: Path,
                 entries: Dict[str, Dict[str, Any]],
                 dynamic_warnings: List[str]) -> None:
        self.filepath = filepath
        self.entries = entries
        self.dynamic_warnings = dynamic_warnings
        # ``import os`` → ``imports["os"] = "os"``.
        # ``import os.path as p`` → ``imports["p"] = "os.path"``.
        # ``from os import path`` → ``imports["path"] = "os.path"``.
        # ``from os.path import join`` → ``imports["join"] = "os.path.join"``.
        self.imports: Dict[str, str] = {}
        # Local name → annotated stdlib type (e.g. ``re.Pattern``).
        # Populated by ``visit_AnnAssign`` and parameter annotations so
        # that ``x.search(...)`` can be attributed to ``re.Pattern.search``.
        self.var_types: Dict[str, str] = {}

    # ----- Imports -------------------------------------------------------

    def _record_import(self, local: str, qualified: str) -> None:
        self.imports[local] = qualified

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            qualified = alias.name
            local = alias.asname or alias.name.split(".", 1)[0]
            self._record_import(local, qualified)
            top = qualified.split(".", 1)[0]
            if top in _STDLIB_TOP_LEVEL:
                e = self.entries.setdefault(qualified, _new_entry(qualified, "module"))
                e["locations"].add(self._loc(node))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is None:
            self.generic_visit(node)
            return
        top = node.module.split(".", 1)[0]
        if top not in _STDLIB_TOP_LEVEL:
            self.generic_visit(node)
            return
        for alias in node.names:
            qualified = f"{node.module}.{alias.name}"
            local = alias.asname or alias.name
            self._record_import(local, qualified)
            e = self.entries.setdefault(qualified, _new_entry(qualified, "module_function"))
            e["locations"].add(self._loc(node))
        self.generic_visit(node)

    # ----- Attribute / Call ---------------------------------------------

    def _resolve_attr_chain(self, node: ast.AST) -> Optional[str]:
        """Walk an Attribute chain to a Name leaf and return the dotted
        path. ``os.path.join`` → ``"os.path.join"``. Returns None when the
        leaf isn't a Name (e.g. a subscript, call, attribute of an
        attribute we don't track)."""
        parts: List[str] = []
        cur = node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
            parts.reverse()
            return ".".join(parts)
        return None

    def visit_Attribute(self, node: ast.Attribute) -> None:
        chain = self._resolve_attr_chain(node)
        if chain is not None:
            head, _, _rest = chain.partition(".")
            qual = self.imports.get(head)
            if qual is not None:
                # Replace the local head with the fully-qualified import path.
                resolved = qual + chain[len(head):] if chain != head else qual
                top = resolved.split(".", 1)[0]
                if top in _STDLIB_TOP_LEVEL:
                    e = self.entries.setdefault(resolved, _new_entry(resolved, "attribute"))
                    e["locations"].add(self._loc(node))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        # Builtins called bare: ``len(x)``, ``range(0, n)``, ``isinstance(...)``.
        if isinstance(node.func, ast.Name) and node.func.id in _BUILTINS:
            name = f"builtins.{node.func.id}"
            e = self.entries.setdefault(name, _new_entry(name, "builtin"))
            e["call_level"] = True
            e["locations"].add(self._loc(node))
        # Method calls on an attribute chain: ``re.compile(...)``,
        # ``json.dumps(...)``, ``os.path.join(...)``, ``x.search(...)``.
        elif isinstance(node.func, ast.Attribute):
            chain = self._resolve_attr_chain(node.func)
            if chain is not None:
                head, _, _rest = chain.partition(".")
                qual = self.imports.get(head)
                if qual is not None:
                    resolved = qual + chain[len(head):] if chain != head else qual
                    top = resolved.split(".", 1)[0]
                    if top in _STDLIB_TOP_LEVEL:
                        e = self.entries.setdefault(
                            resolved, _new_entry(resolved, "module_function"))
                        e["call_level"] = True
                        e["locations"].add(self._loc(node))
                else:
                    # head is a local name. If we have a typed reference,
                    # attribute to that type.
                    typ = self.var_types.get(head)
                    if typ is not None and "." in typ:
                        method = chain.split(".", 1)[1]
                        resolved = f"{typ}.{method}"
                        top = resolved.split(".", 1)[0]
                        if top in _STDLIB_TOP_LEVEL:
                            e = self.entries.setdefault(
                                resolved, _new_entry(resolved, "method"))
                            e["call_level"] = True
                            e["locations"].add(self._loc(node))
                    else:
                        # Unresolvable method (``x.split()`` where x is Any
                        # or unannotated). Workplan §4.3: report a warning.
                        method = chain.split(".", 1)[1] if "." in chain else chain
                        self.dynamic_warnings.append(
                            f"{self._loc(node)} — unresolvable method call "
                            f"`{chain}` (annotate the receiver to surface it).")
        self.generic_visit(node)

    # ----- Type-level exposures (workplan §2.2 case 1) ------------------

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._record_annotation(node.annotation)
        if isinstance(node.target, ast.Name) and isinstance(node.annotation, ast.Attribute):
            chain = self._resolve_attr_chain(node.annotation)
            if chain is not None:
                head = chain.split(".", 1)[0]
                qual = self.imports.get(head)
                if qual is not None:
                    self.var_types[node.target.id] = qual + chain[len(head):]
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for arg in node.args.args:
            if arg.annotation is not None:
                self._record_annotation(arg.annotation)
                # Track typed parameters so subsequent method calls on
                # them can be attributed.
                if isinstance(arg.annotation, ast.Attribute):
                    chain = self._resolve_attr_chain(arg.annotation)
                    if chain is not None:
                        head = chain.split(".", 1)[0]
                        qual = self.imports.get(head)
                        if qual is not None:
                            self.var_types[arg.arg] = qual + chain[len(head):]
                elif isinstance(arg.annotation, ast.Name):
                    self.var_types[arg.arg] = arg.annotation.id
        if node.returns is not None:
            self._record_annotation(node.returns)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef  # noqa: N815

    def _record_annotation(self, node: ast.AST) -> None:
        """Mark a referenced stdlib type as ``type_level=True``."""
        if isinstance(node, ast.Attribute):
            chain = self._resolve_attr_chain(node)
            if chain is not None:
                head = chain.split(".", 1)[0]
                qual = self.imports.get(head)
                if qual is not None:
                    resolved = qual + chain[len(head):] if chain != head else qual
                    top = resolved.split(".", 1)[0]
                    if top in _STDLIB_TOP_LEVEL:
                        e = self.entries.setdefault(
                            resolved, _new_entry(resolved, "class"))
                        e["type_level"] = True
                        e["locations"].add(self._loc(node))
        elif isinstance(node, ast.Name):
            # `typing` re-exports common type names; ``List[str]`` →
            # ``Name(id='List')`` after ``from typing import List``.
            qual = self.imports.get(node.id)
            if qual and qual.startswith("typing."):
                e = self.entries.setdefault(qual, _new_entry(qual, "class"))
                e["type_level"] = True
                e["locations"].add(self._loc(node))
        elif isinstance(node, ast.Subscript):
            self._record_annotation(node.value)
            # Recurse into the slice so `Dict[str, int]` records `str`
            # and `int` if they were tracked.
            if isinstance(node.slice, ast.Tuple):
                for elt in node.slice.elts:
                    self._record_annotation(elt)
            else:
                self._record_annotation(node.slice)

    # ----- Helpers -------------------------------------------------------

    def _loc(self, node: ast.AST) -> str:
        try:
            rel = self.filepath.relative_to(REPO_ROOT)
        except ValueError:
            rel = self.filepath
        return f"{rel}:{getattr(node, 'lineno', 0)}"


# ---------------------------------------------------------------------------
# Top-level discovery
# ---------------------------------------------------------------------------

def discover(roots: Optional[Iterable[Path]] = None
             ) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
    """Walk ``roots`` (default: ``src/pycsl/``) and return the entry map
    plus a list of dynamic-access warning strings (workplan §4.3)."""
    if roots is None:
        roots = [SRC_PYCSL_ROOT]
    entries: Dict[str, Dict[str, Any]] = {}
    warnings: List[str] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            # Skip generated stubs and tests checked into the source tree.
            rel = path.relative_to(REPO_ROOT)
            if any(part.startswith(("test", "tests", "__pycache__")) for part in rel.parts):
                continue
            try:
                tree = ast.parse(path.read_text())
            except SyntaxError as exc:
                warnings.append(f"{rel}: parse error — {exc}")
                continue
            visitor = _StdlibVisitor(path, entries, warnings)
            visitor.visit(tree)
    return entries, warnings


# ---------------------------------------------------------------------------
# Report I/O — minimal TOML emitter (no external deps required)
# ---------------------------------------------------------------------------

_REPORT_HEADER = """# PyCSL stdlib-coverage report
#
# Generated by ``bin/stdlib-coverage.py --discover``. Do NOT hand-edit
# (workplan §11 anti-pattern). Regenerate by re-running the tool after
# any change to src/pycsl/*.py.
#
# See StdlibCoverage_Workplan.md and
# config/skills/pycsl-stdlib-coverage/SKILL.md for the discipline that
# governs this file.

"""


def write_report(entries: Dict[str, Dict[str, Any]], path: Path) -> None:
    """Emit a deterministic-order TOML report."""
    lines: List[str] = [_REPORT_HEADER.rstrip(), ""]
    for name in sorted(entries):
        e = entries[name]
        lines.append(f"[[entry]]")
        lines.append(f'name = "{name}"')
        lines.append(f'kind = "{e["kind"]}"')
        lines.append(f"call_level = {str(e['call_level']).lower()}")
        lines.append(f"type_level = {str(e['type_level']).lower()}")
        locs = sorted(e["locations"])
        if locs:
            lines.append("locations = [")
            for loc in locs:
                lines.append(f'  "{loc}",')
            lines.append("]")
        else:
            lines.append("locations = []")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n")


def read_report(path: Path) -> Dict[str, Dict[str, Any]]:
    """Minimal TOML reader for the report shape this tool writes.
    Does not handle the full TOML spec — only the array-of-tables our
    own emitter produces."""
    out: Dict[str, Dict[str, Any]] = {}
    if not path.exists():
        return out
    current: Optional[Dict[str, Any]] = None
    in_locs = False
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "[[entry]]":
            current = {"locations": set()}
            in_locs = False
            continue
        if current is None:
            continue
        if line == "locations = [":
            in_locs = True
            continue
        if in_locs:
            if line == "]":
                in_locs = False
                continue
            m = re.match(r'\s*"([^"]+)",?\s*$', line)
            if m:
                current["locations"].add(m.group(1))
            continue
        m = re.match(r'(\w+)\s*=\s*(.+)$', line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).rstrip()
        if val.startswith('"') and val.endswith('"'):
            current[key] = val[1:-1]
        elif val in ("true", "false"):
            current[key] = (val == "true")
        elif val == "[]":
            current[key] = set()
        if key == "name":
            out[current["name"]] = current
    return out


# ---------------------------------------------------------------------------
# `--check` mode
# ---------------------------------------------------------------------------
# We don't yet (PR 1) require the english/pycsl/stub artefacts to exist
# in their per-symbol form — that's PR 4+. The --check mode is wired so
# that once PR 4–6 land, the check trips correctly. Pre-PR-4 we accept
# tabular files but emit a notice.

_ENTRY_RE = re.compile(r"^## `([^`]+)`")
_FENCED_HEADING_RE = re.compile(r"^###\s+`([^`]+)`")


def _parse_headings(md_path: Path) -> Set[str]:
    """Return the set of `<name>` strings appearing in any
    `## ` or `### ` heading. Catches per-symbol headings from PR 4/5
    output, and also the legacy tabular files' module-level headings
    (which won't match symbol names — the check helpfully fails)."""
    out: Set[str] = set()
    if not md_path.exists():
        return out
    for line in md_path.read_text().splitlines():
        m = _ENTRY_RE.match(line) or _FENCED_HEADING_RE.match(line)
        if m:
            out.add(m.group(1))
    return out


def _stub_symbol_names() -> Set[str]:
    """Return the set of qualified names declared by stub files. Looks in
    both candidate directories (workplan §0.6 — pre- and post-rename)."""
    out: Set[str] = set()
    for stub_root in stub_dirs():
        if not stub_root.exists():
            continue
        for path in sorted(stub_root.rglob("*.py")):
            module_parts = path.relative_to(stub_root).with_suffix("").parts
            module_name = ".".join(p for p in module_parts if p != "__init__")
            try:
                tree = ast.parse(path.read_text())
            except SyntaxError:
                continue
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if not node.name.startswith("_"):
                        out.add(f"{module_name}.{node.name}" if module_name else node.name)
    return out


def cmd_check(which: str, strict_stubs: bool = False) -> int:
    """Reconcile the report against the artefacts. ``which`` is one of
    ``english``, ``pycsl``, ``stubs``, ``all``.

    When ``strict_stubs`` is False (the default during the scaffold
    phase), missing stub entries are reported as warnings and do not
    affect the exit code. They become hard errors under ``--strict-stubs``,
    typically once PR 6's full regeneration lands.
    """
    if not REPORT_PATH.exists():
        print(f"[!] No report at {REPORT_PATH.relative_to(REPO_ROOT)}; "
              f"run --discover first.")
        return 2
    entries = read_report(REPORT_PATH)
    expected = set(entries)
    rc = 0
    if which in ("english", "all"):
        present = _parse_headings(CALLS_ENGLISH)
        missing = expected - present
        if missing:
            print(f"[!] calls-english.md: {len(missing)} entries missing.")
            for name in sorted(missing)[:10]:
                print(f"    - {name}")
            if len(missing) > 10:
                print(f"    … and {len(missing) - 10} more")
            rc = 1
        else:
            print(f"[+] calls-english.md: all {len(expected)} entries present.")
    if which in ("pycsl", "all"):
        present = _parse_headings(CALLS_PYCSL)
        missing = expected - present
        if missing:
            print(f"[!] calls-pycsl.md: {len(missing)} entries missing.")
            for name in sorted(missing)[:10]:
                print(f"    - {name}")
            if len(missing) > 10:
                print(f"    … and {len(missing) - 10} more")
            rc = 1
        else:
            print(f"[+] calls-pycsl.md: all {len(expected)} entries present.")
    if which in ("stubs", "all"):
        stub_syms = _stub_symbol_names()
        # Filter expected entries to those that look like resolvable
        # function/method paths under a stub (i.e. ``mod.sub.name``).
        # Builtins live under ``builtins.<name>`` and are matched
        # against ``builtins.<name>`` stubs.
        callable_entries = {
            n for n, e in entries.items()
            if e.get("kind") in ("module_function", "builtin", "method", "class")
        }
        # The discovery walker emits some deep dotted paths that aren't
        # real stub symbols (e.g. ``args.foo.split`` where the receiver
        # type can't be resolved). They're useful as discovery signal
        # but spurious as a stub gate. Filter to single-dotted top-level
        # paths for the strict stubs check; the rest are reported as
        # informational coverage gaps.
        single_dot_callables = {n for n in callable_entries if n.count(".") <= 1}
        deep_callables = callable_entries - single_dot_callables
        missing = single_dot_callables - stub_syms
        if missing:
            level = "!" if strict_stubs else "*"
            label = "ERROR" if strict_stubs else "warning"
            print(f"[{level}] Lib stubs ({label}): {len(missing)} top-level entries "
                  f"unstubbed (of {len(single_dot_callables)} expected).")
            for name in sorted(missing)[:10]:
                print(f"    - {name}")
            if len(missing) > 10:
                print(f"    … and {len(missing) - 10} more")
            if strict_stubs:
                rc = 1
        else:
            print(f"[+] Lib stubs: all {len(single_dot_callables)} "
                  f"top-level entries covered.")
        if deep_callables:
            unstubbed_deep = deep_callables - stub_syms
            if unstubbed_deep:
                print(f"[*] {len(unstubbed_deep)} deep dotted paths "
                      f"unresolved (informational — AST walker artefacts; "
                      f"strengthen receiver annotations in src/pycsl/ to surface).")
        # Reverse — dead stubs (workplan §5 step 4 reverse-check). Warn only.
        dead = stub_syms - expected
        if dead:
            print(f"[*] {len(dead)} stub symbols are not in the report "
                  f"(dead-stub candidates). Warning only; promotes to error "
                  f"after three releases of dead-stub status.")
    return rc


# ---------------------------------------------------------------------------
# `--diff` mode
# ---------------------------------------------------------------------------

def cmd_manifest() -> int:
    """Generate ``src/pycsl_lib/MANIFEST.toml`` from the on-disk stubs.

    Lists every stub file, every public symbol, the Python version
    targeted, and a content hash per file (workplan §3.3). The manifest
    is the CI-drift detector for stub content.
    """
    import hashlib
    stub_root = stub_dirs()[0]
    if not stub_root.exists():
        print(f"[!] No stub directory at {stub_root.relative_to(REPO_ROOT)}.")
        return 2
    lines: List[str] = [
        "# PyCSL stub manifest",
        "#",
        "# Generated by ``bin/stdlib-coverage.py --manifest``. Lists every",
        "# stub file in ``src/pycsl_lib/``, its public symbols, the Python",
        "# version targeted, and a content hash for CI drift detection.",
        "# See workplan §3.3.",
        "",
        'python_version = "3.16-alpha"  # cpython/ submodule HEAD',
        "",
    ]
    for path in sorted(stub_root.rglob("*.py")):
        rel = path.relative_to(stub_root)
        module_parts = rel.with_suffix("").parts
        module_name = ".".join(p for p in module_parts if p != "__init__")
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError as exc:
            print(f"[!] {rel}: parse error — {exc}")
            continue
        symbols = sorted({
            node.name for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and not node.name.startswith("_")
        })
        content_hash = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        lines.append("[[stub]]")
        lines.append(f'path = "{rel}"')
        lines.append(f'module = "{module_name}"')
        lines.append(f'sha256_prefix = "{content_hash}"')
        if symbols:
            lines.append("symbols = [")
            for s in symbols:
                lines.append(f'  "{s}",')
            lines.append("]")
        else:
            lines.append("symbols = []")
        lines.append("")
    manifest_path = stub_root / "MANIFEST.toml"
    manifest_path.write_text("\n".join(lines).rstrip() + "\n")
    print(f"[+] Manifest written to {manifest_path.relative_to(REPO_ROOT)}.")
    return 0


def cmd_scaffold(which: str) -> int:
    """Emit a per-symbol skeleton ``calls-english.md`` or
    ``calls-pycsl.md`` from the discovery report.

    Each entry produces a ``## `<name>`` heading with placeholder
    English / contract content marked ``TODO``. Designed as the
    initial scaffold per workplan §13 steps 4 and 5 — the hand
    curation of real prose and contracts is the multi-week labor
    that follows; this gets the structure in place so the check
    modes can be wired immediately."""
    if not REPORT_PATH.exists():
        print(f"[!] No report at {REPORT_PATH.relative_to(REPO_ROOT)}; "
              f"run --discover first.")
        return 2
    entries = read_report(REPORT_PATH)
    out_path = CALLS_ENGLISH if which == "english" else CALLS_PYCSL
    grouped: Dict[str, List[str]] = {}
    for name in sorted(entries):
        # Group by top-level module so the file reads in module order.
        top = name.split(".", 1)[0]
        grouped.setdefault(top, []).append(name)
    lines: List[str] = []
    if which == "english":
        lines.extend([
            "# Library Method Calls — English Descriptions",
            "",
            "Per-symbol English descriptions for every stdlib API entry used",
            "inside `src/pycsl/`. Anchored to vendored CPython docs at the",
            "submodule HEAD (Python 3.16-alpha at the time of scaffolding).",
            "",
            "Each entry follows the workplan §3.1 template:",
            "",
            "```",
            "## `<qualified.name>`",
            "<English description, anchored to CPython doc paragraph>.",
            "Raises: <exceptions> | nothing",
            "Source: cpython/Doc/library/<module>.rst",
            "Modeled in: src/pycsl_lib/<module>.py",
            "PyCSL contract: calls-pycsl.md#<anchor>",
            "```",
            "",
            "**Status:** scaffolded. Entries marked `TODO` need hand-written",
            "English from the CPython doc files. See workplan §13 step 4 and",
            "`config/skills/pycsl-stdlib-coverage/SKILL.md` for the curation",
            "discipline.",
            "",
            "---",
            "",
        ])
    else:  # pycsl
        lines.extend([
            "# Library Method Calls — PyCSL Contracts",
            "",
            "Per-symbol PyCSL contract for every stdlib API entry used inside",
            "`src/pycsl/`. The contract is the source of truth for proof",
            "generation; the English in `calls-english.md` is the source of",
            "truth for *what the contract is supposed to mean*.",
            "",
            "Each entry follows the workplan §3.2 template:",
            "",
            "    ## `<qualified.name>`",
            "    ```python",
            "    #@ requires <expr>",
            "    #@ ensures <expr>",
            "    #@ assigns <targets> | \\nothing",
            "    #@ raises { <ExcA>, <ExcB> } | raises { }",
            "    #@ \\trusted",
            "    def <name>(...) -> <ret>: ...",
            "    ```",
            "    Cross-check: read the contract above and rewrite it in",
            "    English; compare to calls-english.md.",
            "",
            "**Status:** scaffolded with `TODO` contracts. The `raises { }`",
            "clause is mandatory per workplan §8.3 — empty braces when total.",
            "Hand curation pending; see workplan §13 step 5.",
            "",
            "---",
            "",
        ])
    for top in sorted(grouped):
        lines.append(f"## Module — `{top}`")
        lines.append("")
        for name in grouped[top]:
            e = entries[name]
            kind = e.get("kind", "module_function")
            lines.append(f"## `{name}`")
            lines.append("")
            if which == "english":
                lines.append(f"TODO — describe `{name}` in plain English, anchored to CPython doc.")
                lines.append("")
                lines.append(f"Raises: TODO")
                # The CPython doc path follows the convention
                # `cpython/Doc/library/<top-level-module>.rst`. For
                # dotted modules like `os.path` the doc still lives in
                # `os.path.rst` at the top of the Doc tree.
                doc_module = top if top != "builtins" else "functions"
                lines.append(f"Source: cpython/Doc/library/{doc_module}.rst (Python 3.16-alpha)")
                modeled = f"src/pycsl_lib/{top}.py" if "." not in name else \
                    f"src/pycsl_lib/{name.rsplit('.', 1)[0].replace('.', '/')}.py"
                lines.append(f"Modeled in: {modeled}")
                anchor = name.replace(".", "").lower()
                lines.append(f"PyCSL contract: calls-pycsl.md#{anchor}")
            else:
                # Workplan §3.2 template, with mandatory raises {}.
                lines.append("```python")
                lines.append(f"#@ requires True  # TODO")
                lines.append(f"#@ ensures True  # TODO")
                lines.append(f"#@ assigns \\nothing  # TODO")
                lines.append(f"#@ raises {{ }}  # TODO — fill in raised exceptions per CPython docs")
                lines.append(f"#@ \\trusted")
                py_name = name.rsplit(".", 1)[-1]
                if kind == "class":
                    lines.append(f"class {py_name}: ...")
                else:
                    lines.append(f"def {py_name}(*args, **kwargs) -> int: ...")
                lines.append("```")
                lines.append("")
                lines.append("Cross-check: TODO — verify the contract above is faithful to "
                             f"`calls-english.md#{name.replace('.', '').lower()}`.")
            lines.append("")
        lines.append("---")
        lines.append("")
    out_path.write_text("\n".join(lines).rstrip() + "\n")
    print(f"[+] Scaffolded {len(entries)} entries into "
          f"{out_path.relative_to(REPO_ROOT)}.")
    return 0


def cmd_diff(baseline_path: Path) -> int:
    """Compare the on-disk baseline to a fresh discovery. Print added /
    removed / changed entries."""
    if not baseline_path.exists():
        print(f"[!] No baseline at {baseline_path.relative_to(REPO_ROOT)}.")
        return 2
    baseline = read_report(baseline_path)
    fresh_entries, _ = discover()
    fresh: Dict[str, Dict[str, Any]] = {}
    for name, e in fresh_entries.items():
        e2 = dict(e)
        e2["locations"] = sorted(e["locations"])
        fresh[name] = e2
    added = sorted(set(fresh) - set(baseline))
    removed = sorted(set(baseline) - set(fresh))
    print(f"[*] Added: {len(added)}; removed: {len(removed)}.")
    for name in added:
        print(f"    +{name}")
    for name in removed:
        print(f"    -{name}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="PyCSL stdlib-coverage discovery and check tool.")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_disc = sub.add_parser("--discover".lstrip("-"),
                             help="Walk src/pycsl/ and write the report.")
    p_disc.add_argument("--output", "-o", type=Path, default=REPORT_PATH,
                        help="Output report path (default: stdlib-coverage-report.toml).")
    p_disc.add_argument("--self-test", action="store_true",
                        help="Run a small self-test on src/pycsl/errors.py only.")
    p_disc.add_argument("--show-warnings", action="store_true",
                        help="Print dynamic-access warnings to stderr.")

    p_check = sub.add_parser("--check".lstrip("-"),
                              help="Reconcile the report against the artefacts.")
    p_check.add_argument("which", choices=("english", "pycsl", "stubs", "all"),
                         default="all", nargs="?")
    p_check.add_argument("--strict-stubs", action="store_true",
                          help="Treat missing stub entries as hard errors. "
                               "Default is warning-only during the scaffold phase.")

    p_diff = sub.add_parser("--diff".lstrip("-"),
                             help="Diff the report against a baseline TOML.")
    p_diff.add_argument("baseline", type=Path, nargs="?", default=REPORT_PATH,
                        help="Baseline report (default: stdlib-coverage-report.toml).")

    p_scaf = sub.add_parser("--scaffold".lstrip("-"),
                             help="Emit a skeleton calls-english.md or calls-pycsl.md "
                                  "from the report. Workplan §13 steps 4/5.")
    p_scaf.add_argument("which", choices=("english", "pycsl"),
                        help="Which artefact to scaffold.")

    sub.add_parser("--manifest".lstrip("-"),
                    help="Generate src/pycsl_lib/MANIFEST.toml from the "
                         "on-disk stubs. Workplan §3.3.")

    # Allow the "--mode" style argv too: turn "--discover" → "discover".
    if argv is None:
        argv = sys.argv[1:]
    argv = [a.lstrip("-") if a.startswith("--") and a in
            ("--discover", "--check", "--diff", "--scaffold", "--manifest")
            else a for a in argv]
    args = parser.parse_args(argv)

    if args.mode == "discover":
        roots = [SRC_PYCSL_ROOT / "errors.py"] if args.self_test else None
        entries, warnings = discover(roots)
        # Convert sets to lists for stable output.
        for e in entries.values():
            e["locations"] = sorted(e["locations"])
        write_report(entries, args.output)
        print(f"[+] {len(entries)} stdlib entries written to "
              f"{args.output.relative_to(REPO_ROOT)}.")
        if args.show_warnings and warnings:
            print(f"[*] {len(warnings)} warnings:", file=sys.stderr)
            for w in warnings[:50]:
                print(f"    {w}", file=sys.stderr)
        return 0

    if args.mode == "check":
        return cmd_check(args.which, strict_stubs=getattr(args, "strict_stubs", False))

    if args.mode == "diff":
        return cmd_diff(args.baseline)

    if args.mode == "scaffold":
        return cmd_scaffold(args.which)

    if args.mode == "manifest":
        return cmd_manifest()

    return 2


if __name__ == "__main__":
    sys.exit(main())
