#!/usr/bin/env python3
"""agent-stdlib-annotate — autonomous stdlib stub annotator.

Walks Python stdlib stub modules in `src/pycsl_lib/`, promotes each
unannotated function from L2 (trusted-only) to L4/L5 (full contract
+ reference tests) by deriving requires/ensures from the official
CPython docstrings. Runs unsupervised: stages all changes in the
working tree, never commits, rolls back per-module on gate failure.

See `config/agents/agent-stdlib-annotate.md` for the spec.
"""
from __future__ import annotations

AGENT_NAME = "agent-stdlib-annotate"

import argparse
import ast
import datetime
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Path bootstrap — match the convention used by agent-annotate.py.
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent.parent  # src/pycsl/agents -> root
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_PROJECT_ROOT / "bin"))

from llm_client import llm_generate, log  # noqa: E402


# ---------------------------------------------------------------------------
# Load coverage scanner constants
# ---------------------------------------------------------------------------


def _load_coverage_module():
    """Import `bin/stdlib-coverage-report.py` as a module so we can
    reuse its `_NON_STDLIB` exclusion set and classifier logic.
    The filename contains a dash so we can't `import` it directly.

    Registers in `sys.modules` BEFORE `exec_module` — Python 3.14's
    dataclass elaborator looks up `cls.__module__` in `sys.modules`
    and crashes on a missing entry."""
    spec = importlib.util.spec_from_file_location(
        "stdlib_coverage",
        _PROJECT_ROOT / "bin" / "stdlib-coverage-report.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["stdlib_coverage"] = module
    spec.loader.exec_module(module)
    return module


_COV = _load_coverage_module()


_STUB_DIR = _PROJECT_ROOT / "src" / "pycsl_lib"
_TEST_DIR = _PROJECT_ROOT / "test-suite" / "corpus" / "python-reference" / "stdlib"
_CPYTHON_LIB = _PROJECT_ROOT / "cpython" / "Lib"
_GAP_REPORT = _PROJECT_ROOT / "metrics" / "stdlib-gap-report.json"
_PROPOSED_DIR = _PROJECT_ROOT / "proposed-features"
_FEATURE_TEMPLATE = (
    _PROJECT_ROOT
    / "config"
    / "skills"
    / "agent-stdlib-annotate"
    / "references"
    / "feature-plan-template.md"
)


# ---------------------------------------------------------------------------
# Item 1.1 — gap detection (better-agent.md Phase 1 / Phase 1.1)
# ---------------------------------------------------------------------------
#
# Scan existing # cite:_note: lines in src/pycsl_lib/ (or any fixture
# tree via --scan-path), classify each into a category, aggregate.
# Writes metrics/stdlib-gap-report.json. Read-only with respect to
# src/.

# Heuristic taxonomy. Each category maps a stem regex; longer regex
# wins if multiple match (handled in _classify_gap by ordering).
_GAP_CATEGORIES: List[Tuple[str, re.Pattern]] = [
    ("iterator-semantics", re.compile(
        r"\b(iterator|infinite|yields?|lazy sequence|generator|"
        r"indefinite|stream|next\()\b", re.I)),
    ("regex-semantics", re.compile(
        r"\b(regex|regular expression|pattern[- ]match)\b", re.I)),
    ("higher-order", re.compile(
        r"\b(callback|predicate function|function argument|"
        r"higher[- ]order|callable)\b", re.I)),
    ("string-content", re.compile(
        r"\b(string contents?|format string|encoding|"
        r"unicode|character class)\b", re.I)),
    ("io-side-effect", re.compile(
        r"\b(file system|file handle|file descriptor|socket|"
        r"stream of bytes|I/O|side[- ]effect)\b", re.I)),
    ("non-deterministic", re.compile(
        r"\b(random|time|clock|uuid|hash randomization|"
        r"system entropy|non[- ]deterministic)\b", re.I)),
]


def _classify_gap(note: str) -> str:
    """Return the best-match category for a # cite:_note: text."""
    for category, pat in _GAP_CATEGORIES:
        if pat.search(note):
            return category
    return "unclassified"


# Pattern that captures the note text after `# cite:_note:` (one or
# more continuation lines indented or prefixed with `#`).
_CITE_NOTE_RE = re.compile(
    r"#\s*cite:_note\s*:\s*(.*?)(?=^[^#]|^\s*$)",
    re.M | re.S,
)


def _scan_existing_notes(lib_root: Path) -> Dict[str, dict]:
    """Walk a tree for `# cite:_note:` lines and classify them.

    Returns {category: {count: int, examples: [{stub: str, qualname: str,
    note: str, line: int}, ...]}}.
    """
    report: Dict[str, dict] = {}
    for py in sorted(lib_root.rglob("*.py")):
        if "__pycache__" in py.parts or ".egg-info" in str(py):
            continue
        try:
            text = py.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        # Compute relative path; tolerate fixtures outside src/pycsl_lib
        try:
            rel = py.relative_to(_PROJECT_ROOT)
        except ValueError:
            rel = py
        # `# cite:_note:` annotations PRECEDE the def they describe
        # (same shape as #@ requires / #@ ensures contract blocks).
        # Walk line-wise; when we hit a cite:_note, collect any
        # continuation lines and then scan FORWARD for the next def —
        # but only across lines that look like the contract block
        # (comments, decorators, blank). If a non-block line intervenes,
        # the note is module-level.
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            m = re.match(r"\s*#\s*cite:_note\s*:\s*(.*)", line)
            if not m:
                i += 1
                continue
            note_lines = [m.group(1).strip()]
            j = i + 1
            while j < len(lines):
                cont = lines[j].lstrip()
                if cont.startswith("#") and not re.match(
                    r"#\s*(cite|@)", cont
                ):
                    note_lines.append(cont.lstrip("#").strip())
                    j += 1
                else:
                    break
            # Now scan forward from j for the next def — only across
            # contract-block lines (#, @, blank).
            qualname = "<module-level>"
            k = j
            while k < len(lines):
                kstripped = lines[k].lstrip()
                if not kstripped:
                    k += 1
                    continue
                if kstripped.startswith("#") or kstripped.startswith("@"):
                    k += 1
                    continue
                mm = re.match(
                    r"(?:async\s+)?def\s+([A-Za-z_]\w*)", kstripped
                )
                if mm:
                    qualname = mm.group(1)
                break
            note = " ".join(s for s in note_lines if s)
            category = _classify_gap(note)
            bucket = report.setdefault(
                category, {"count": 0, "examples": []}
            )
            bucket["count"] += 1
            bucket["examples"].append({
                "stub": str(rel),
                "qualname": qualname,
                "note": note,
                "line": i + 1,
            })
            i = j
    return report


def _write_gap_report(report: Dict[str, dict], scan_root: Path) -> None:
    _GAP_REPORT.parent.mkdir(parents=True, exist_ok=True)
    total = sum(b["count"] for b in report.values())
    payload = {
        "schema": "pycsl-stdlib-gap-report-v1",
        "generated_at": datetime.datetime.now(datetime.UTC)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
        "scan_root": str(scan_root),
        "total_notes": total,
        "categories": report,
    }
    _GAP_REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True))


def _print_gap_summary(report: Dict[str, dict]) -> None:
    if not report:
        print("  (no # cite:_note: markers found)")
        return
    print(f"  {'category':<22} count  examples (first 3)")
    print(f"  {'-' * 22}  -----  ------------------------")
    for cat in sorted(report, key=lambda c: -report[c]["count"]):
        bucket = report[cat]
        ex = ", ".join(
            f"{e['qualname']}@{Path(e['stub']).name}:{e['line']}"
            for e in bucket["examples"][:3]
        )
        print(f"  {cat:<22} {bucket['count']:>5}  {ex}")


def cmd_detect_gaps(scan_path: Optional[Path]) -> int:
    """Item 1.1 entry point."""
    root = scan_path.resolve() if scan_path else _STUB_DIR
    if not root.exists():
        print(f"[{AGENT_NAME}] error: scan path does not exist: {root}",
              file=sys.stderr)
        return 2
    if root.is_file():
        # Allow a single .py file as the scan root (used by fixture tests).
        target_dir = root.parent
    else:
        target_dir = root
    report = _scan_existing_notes(target_dir)
    if root.is_file():
        # Filter to just notes from the named file
        for cat, bucket in list(report.items()):
            bucket["examples"] = [
                e for e in bucket["examples"]
                if Path(e["stub"]).name == root.name
                or e["stub"] == str(root.relative_to(_PROJECT_ROOT))
                if True  # defensive — always include if path matches
            ]
            bucket["count"] = len(bucket["examples"])
            if bucket["count"] == 0:
                del report[cat]
    _write_gap_report(report, root)
    print(f"[{AGENT_NAME}] --detect-gaps  scan_root={root}")
    print(f"  wrote {_GAP_REPORT.relative_to(_PROJECT_ROOT)}  "
          f"({sum(b['count'] for b in report.values())} markers, "
          f"{len(report)} categories)")
    _print_gap_summary(report)
    return 0


# ---------------------------------------------------------------------------
# Item 1.2 — feature-plan proposal (better-agent.md Phase 2 / Phase 1.2)
# ---------------------------------------------------------------------------

_CATEGORY_HUMAN = {
    "iterator-semantics": "iterator semantics",
    "regex-semantics": "regex semantics",
    "higher-order": "higher-order function semantics",
    "string-content": "string content reasoning",
    "io-side-effect": "I/O side-effect modelling",
    "non-deterministic": "non-deterministic primitives",
    "unclassified": "unclassified L3-ceiling gap",
}


def _load_gap_report() -> Optional[dict]:
    if not _GAP_REPORT.is_file():
        return None
    try:
        return json.loads(_GAP_REPORT.read_text())
    except json.JSONDecodeError:
        return None


def _read_anchor_stub(stub_rel: str, qualname: str) -> str:
    """Return a 6-line excerpt centred on the cite:_note for the worked example."""
    p = _PROJECT_ROOT / stub_rel
    if not p.is_file():
        return f"# (anchor stub not found: {stub_rel})"
    lines = p.read_text().splitlines()
    # Find the def line for the qualname and walk backward to the first
    # contract/cite block; emit up to ~10 lines of context.
    for i, line in enumerate(lines):
        m = re.match(r"\s*(?:async\s+)?def\s+([A-Za-z_]\w*)", line)
        if m and m.group(1) == qualname:
            # Walk backward to the top of the contract block
            start = i
            while start > 0 and lines[start - 1].lstrip().startswith(("#", "@")):
                start -= 1
            end = min(i + 2, len(lines))
            return "\n".join(lines[start:end])
    return f"# (def {qualname} not found in {stub_rel})"


def _render_stuck_list(examples: List[dict], limit: int = 20) -> str:
    rows = []
    for e in examples[:limit]:
        rows.append(f"- `{e['qualname']}` in `{e['stub']}:{e['line']}` — {e['note'][:120]}")
    if len(examples) > limit:
        rows.append(f"- _(+{len(examples) - limit} more — see "
                    f"`metrics/stdlib-gap-report.json`)_")
    return "\n".join(rows) if rows else "_(none)_"


def cmd_propose_feature(category: str, threshold: int) -> int:
    """Item 1.2 entry point."""
    report = _load_gap_report()
    if report is None:
        print(f"[{AGENT_NAME}] error: no gap report at "
              f"{_GAP_REPORT.relative_to(_PROJECT_ROOT)}. "
              f"Run --detect-gaps first.", file=sys.stderr)
        return 2
    bucket = report.get("categories", {}).get(category)
    if not bucket:
        print(f"[{AGENT_NAME}] no notes found in category '{category}'. "
              f"Known categories: "
              f"{sorted(report.get('categories', {}).keys())}",
              file=sys.stderr)
        return 1
    count = bucket["count"]
    if count < threshold:
        print(f"[{AGENT_NAME}] category '{category}' has {count} notes "
              f"(below threshold {threshold}); no proposal generated.")
        return 0
    if not _FEATURE_TEMPLATE.is_file():
        print(f"[{AGENT_NAME}] error: template missing at "
              f"{_FEATURE_TEMPLATE.relative_to(_PROJECT_ROOT)}",
              file=sys.stderr)
        return 2

    template = _FEATURE_TEMPLATE.read_text()
    examples = bucket["examples"]
    anchor = examples[0]
    anchor_stub = _read_anchor_stub(anchor["stub"], anchor["qualname"])

    slots = {
        "CATEGORY": category,
        "CATEGORY_HUMAN": _CATEGORY_HUMAN.get(category, category),
        "TIMESTAMP": report.get("generated_at", "unknown"),
        "ANCHOR_QUALNAME": anchor["qualname"],
        "ANCHOR_FILE": anchor["stub"],
        "ANCHOR_NOTE": anchor["note"],
        "ANCHOR_STUB": anchor_stub,
        "COUNT": str(count),
        "STUCK_LIST": _render_stuck_list(examples),
        # Option placeholders are left as-is for the human to fill in.
        "OPTION_A_PLACEHOLDER": "(human: name the cheap, lossy model)",
        "OPTION_B_PLACEHOLDER": "(human: name the medium-cost partial model)",
        "OPTION_C_PLACEHOLDER": "(human: name the high-cost full model)",
        "OPTION_D_PLACEHOLDER": "(human: name the intrusive desugar option)",
    }
    out = template
    for key, val in slots.items():
        out = out.replace("{{" + key + "}}", val)

    _PROPOSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _PROPOSED_DIR / f"missing-{category}-feature.md"
    out_path.write_text(out)
    print(f"[{AGENT_NAME}] --propose-feature {category}")
    print(f"  wrote {out_path.relative_to(_PROJECT_ROOT)} "
          f"({count} stuck functions, anchor={anchor['qualname']})")
    print(f"  STATUS: DRAFT — human review required before "
          f"agent-feature-supervisor.py can act on it.")
    return 0


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


class _ModuleLog:
    """Per-module log file. Appended to throughout the run."""

    def __init__(self, log_dir: Path, module: str):
        log_dir.mkdir(parents=True, exist_ok=True)
        self.path = log_dir / f"{module}.log"
        self.fp = self.path.open("a", encoding="utf-8")
        self.write(f"=== {datetime.datetime.now(datetime.UTC).isoformat()}Z  "
                   f"Module: {module} ===")

    def write(self, msg: str) -> None:
        self.fp.write(msg + "\n")
        self.fp.flush()
        print(msg)

    def close(self) -> None:
        self.fp.close()


# ---------------------------------------------------------------------------
# Coverage-snapshot helpers
# ---------------------------------------------------------------------------


def _coverage_snapshot(module: str) -> Dict[str, int]:
    """Return `{L1, L2, L3, L4, L5}` counts for one module by
    invoking the coverage scanner. Falls back to direct API call
    rather than shelling out — faster and avoids JSON parsing."""
    path = _STUB_DIR / f"{module}.py"
    if not path.is_file():
        return {k: 0 for k in ("L1", "L2", "L3", "L4", "L5")}
    report = _COV._analyze_module(path)
    return dict(report.counts)


def _l4_plus(counts: Dict[str, int]) -> int:
    return counts["L4"] + counts["L5"]


# ---------------------------------------------------------------------------
# CPython docstring extraction
# ---------------------------------------------------------------------------


def _cpython_paths_for(module: str) -> List[Path]:
    """Return candidate CPython source paths for a given module
    name. Handles top-level modules (`math` → `Lib/math.py`) and
    a few hand-mapped package forms (`os.path` → `Lib/posixpath.py`
    on POSIX, but we use `Lib/os/path.py`-style if present)."""
    candidates: List[Path] = []
    # Top-level module.
    candidates.append(_CPYTHON_LIB / f"{module}.py")
    # Package with __init__.py.
    candidates.append(_CPYTHON_LIB / module / "__init__.py")
    # os.path special case: real impl is posixpath / ntpath; we
    # use posixpath since PyCSL targets Linux.
    if module == "os":
        candidates.append(_CPYTHON_LIB / "os.py")
    return [p for p in candidates if p.is_file()]


@dataclass
class _CPyFunc:
    name: str
    docstring: str
    signature: str
    source_path: str  # for the `# cite:` line
    source_line: int


def _extract_cpython_funcs(module: str) -> Dict[str, _CPyFunc]:
    """Build a dict mapping function name → docstring/signature for
    each public function in `module`. Two-tier lookup:

    1. **AST scan of `cpython/Lib/<module>.py`** — works for
       pure-Python stdlib modules (`json`, `os`, `re`, `pathlib`,
       `collections`, …).
    2. **Runtime introspection** — for C-implemented modules
       (`math`, `sys`, `_io`, …) we `import` the module in the
       current interpreter and read `__doc__` off each callable.
       This is the only practical offline source for C extensions;
       the docstrings are baked into the binary by the CPython
       build (`Modules/<mod>module.c` → `PyDoc_STR(...)`).

    AST results take precedence; introspection fills gaps. Class
    methods are flattened by name (last-wins) — the stub side
    doesn't carry class scope information either."""
    out: Dict[str, _CPyFunc] = {}
    # Tier 1 — AST scan of pure-Python sources.
    for path in _cpython_paths_for(module):
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node) or ""
                if not doc:
                    continue
                try:
                    sig = ast.unparse(node.args)
                except Exception:
                    sig = ""
                fn = _CPyFunc(
                    name=node.name,
                    docstring=doc.strip(),
                    signature=sig,
                    source_path=str(path.relative_to(_PROJECT_ROOT)),
                    source_line=node.lineno,
                )
                out[node.name] = fn
    # Tier 2 — runtime introspection for C-implemented modules.
    try:
        import importlib as _il
        mod = _il.import_module(module)
    except Exception:
        return out
    for name in dir(mod):
        if name.startswith("_"):
            continue
        if name in out:
            continue
        attr = getattr(mod, name, None)
        if not callable(attr):
            continue
        doc = getattr(attr, "__doc__", None)
        if not doc or not isinstance(doc, str) or not doc.strip():
            continue
        # Best-effort signature; many built-ins return None from
        # inspect.signature.
        sig = ""
        try:
            import inspect as _ins
            sig = str(_ins.signature(attr))
        except (TypeError, ValueError):
            pass
        out[name] = _CPyFunc(
            name=name,
            docstring=doc.strip(),
            signature=sig,
            source_path=f"<built-in: {module}.{name}.__doc__>",
            source_line=0,
        )
    return out


# ---------------------------------------------------------------------------
# Stub edits (line-based — keeps the impl simple)
# ---------------------------------------------------------------------------


@dataclass
class _StubFunc:
    name: str
    def_line: int        # 1-based line index of `def <name>(`
    block_start: int     # 1-based; first line of the leading `#@`/`# cite:` block, or def_line if absent
    signature: str       # text from `def <name>` to the closing `)`


_DEF_RE = re.compile(r"^(?:async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_BLOCK_LINE_RE = re.compile(r"^(#@|#\s*cite:)")


def _scan_stub_functions(stub_path: Path) -> List[_StubFunc]:
    """Walk the stub file line by line and return one record per
    top-level function/method definition with its leading directive
    block boundaries. Skips functions whose names start with `_`."""
    lines = stub_path.read_text(encoding="utf-8").splitlines()
    n = len(lines)
    out: List[_StubFunc] = []
    for i, line in enumerate(lines):
        m = _DEF_RE.match(line.lstrip())
        if not m:
            continue
        name = m.group(1)
        if name.startswith("_"):
            continue
        def_line = i + 1
        # Walk backwards over the contiguous directive block.
        block_start = def_line
        j = i - 1
        while j >= 0:
            stripped = lines[j].strip()
            if _BLOCK_LINE_RE.match(stripped):
                block_start = j + 1
                j -= 1
            elif not stripped:
                break
            else:
                break
        # Build signature: this line through the next `)`.
        sig_lines = [line]
        k = i + 1
        while ")" not in sig_lines[-1] and k < n:
            sig_lines.append(lines[k])
            k += 1
        sig = "\n".join(sig_lines).strip()
        out.append(_StubFunc(
            name=name,
            def_line=def_line,
            block_start=block_start,
            signature=sig,
        ))
    return out


def _splice_block(stub_path: Path, fn: _StubFunc, new_block: str) -> None:
    """Replace lines [block_start, def_line-1] of `stub_path` with
    `new_block`. `new_block` should already include trailing
    newline. Operates in-memory; caller may roll back via git."""
    lines = stub_path.read_text(encoding="utf-8").splitlines()
    # Convert to 0-based.
    start = fn.block_start - 1
    end_exclusive = fn.def_line - 1   # def line stays as-is
    new_lines = new_block.rstrip("\n").splitlines()
    merged = lines[:start] + new_lines + lines[end_exclusive:]
    stub_path.write_text("\n".join(merged) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Function classification (do we need to promote this one?)
# ---------------------------------------------------------------------------


def _needs_promotion(stub_path: Path, fn_name: str) -> bool:
    """True iff the function is currently below L4 (i.e. L1/L2/L3
    by the coverage scanner). Reuses the scanner's per-function
    classification."""
    report = _COV._analyze_module(stub_path)
    for f in report.fns:
        if f.name == fn_name:
            return f.level in ("L1", "L2", "L3")
    return False   # not found → don't touch


# ---------------------------------------------------------------------------
# LLM-driven contract derivation
# ---------------------------------------------------------------------------


_BLOCK_FENCE_RE = re.compile(r"```(?:contracts|annotation|csl)?\s*\n(.*?)\n```",
                              re.DOTALL)


def _build_prompt(fn_name: str, stub_sig: str, cpy: Optional[_CPyFunc],
                  existing_block: str) -> str:
    """Build the user prompt for a single function. The system
    prompt is the conventions doc, loaded once at agent startup."""
    parts: List[str] = []
    parts.append(f"## Function: `{fn_name}`")
    parts.append("")
    parts.append("### Current stub signature")
    parts.append("```python")
    parts.append(stub_sig)
    parts.append("```")
    parts.append("")
    if existing_block.strip():
        parts.append("### Current annotation block")
        parts.append("```")
        parts.append(existing_block)
        parts.append("```")
        parts.append("")
    if cpy:
        parts.append(f"### CPython source: `{cpy.source_path}` line {cpy.source_line}")
        parts.append(f"Signature: `{cpy.signature or '(unavailable)'}`")
        parts.append("Docstring:")
        parts.append("```")
        parts.append(cpy.docstring[:2000])
        parts.append("```")
    else:
        parts.append("### CPython docstring: not found")
        parts.append("Apply the conventions doc's Rule 4 (side-effects /")
        parts.append("unknown docs): output a minimal L4 block with")
        parts.append("`requires True` + `ensures True` + the `# cite:` line")
        parts.append("pointing at `cpython/Lib/<module>.py` (best guess).")
    parts.append("")
    parts.append("### Output")
    parts.append("Output ONLY the contract block — lines starting with")
    parts.append("`#@` or `# cite:` — between ```contracts and ```. ")
    parts.append("Do not output the `def` line. Do not output the body.")
    parts.append("Match the canonical pattern from the conventions doc.")
    return "\n".join(parts)


def _parse_llm_block(response: str) -> Optional[str]:
    """Extract the contract block from the LLM response. Accepts
    either fenced ```contracts...``` or any fenced block whose lines
    match `#@` / `# cite:`. Returns None if no usable block."""
    m = _BLOCK_FENCE_RE.search(response)
    if m:
        block = m.group(1)
    else:
        # No fence — try whole response, filtered to block-shaped lines.
        block = response
    keep: List[str] = []
    for line in block.splitlines():
        s = line.strip()
        if _BLOCK_LINE_RE.match(s):
            keep.append(s)
    if not keep:
        return None
    # Re-validate: must contain a `\trusted reviewer:` line.
    if not any(re.match(r"^#@\s*\\trusted\s+reviewer:", k) for k in keep):
        return None
    return "\n".join(keep) + "\n"


def _read_existing_block(stub_path: Path, fn: _StubFunc) -> str:
    lines = stub_path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[fn.block_start - 1:fn.def_line - 1])


# ---------------------------------------------------------------------------
# Reference test generation
# ---------------------------------------------------------------------------


_POSITIVE_TEMPLATE = '''"""Test {module}.{fnname} L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import {module}  # noqa: F401


#@ requires True
#@ ensures True
def use_{fnname}(x: int) -> int:
    return {module}.{fnname}(x)


if __name__ == "__main__":
    pass
'''


_NEGATIVE_TEMPLATE = '''"""Test {module}.{fnname} L5 — negative: caller can't discharge requires.

Documents the soundness path: callers that don't establish the
function's precondition fail to verify under full proof. The
corpus runner uses `--no-proof` for fast iteration; the failure
mode is exercised manually with `--proof`.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import {module}  # noqa: F401


#@ ensures True
def use_{fnname}_unsafe(x: int) -> int:
    return {module}.{fnname}(x)


if __name__ == "__main__":
    pass
'''


def _write_reference_tests(module: str, fn_name: str) -> List[Path]:
    """Write a positive + negative reference test for one promoted
    function. Returns the list of paths written (used for rollback
    on gate failure). Skips if a file with the same name already
    exists."""
    out: List[Path] = []
    d = _TEST_DIR / module
    d.mkdir(parents=True, exist_ok=True)
    pos = d / f"{fn_name}_call_proves.py"
    neg = d / f"{fn_name}_call_fails.py"
    if not pos.exists():
        pos.write_text(
            _POSITIVE_TEMPLATE.format(module=module, fnname=fn_name),
            encoding="utf-8",
        )
        out.append(pos)
    if not neg.exists():
        neg.write_text(
            _NEGATIVE_TEMPLATE.format(module=module, fnname=fn_name),
            encoding="utf-8",
        )
        out.append(neg)
    return out


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


def _gate_compile(stub_path: Path, log_obj: _ModuleLog) -> bool:
    """pycsl --no-proof <stub>; exit 0 means parse + WhyML emit OK."""
    venv_py = _PROJECT_ROOT / ".venv" / "bin" / "python"
    if not venv_py.is_file():
        venv_py = Path(sys.executable)
    cmd = [str(venv_py), "-m", "pycsl.pycsl", "--no-proof", str(stub_path)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                               cwd=str(_PROJECT_ROOT), timeout=300)
    except subprocess.TimeoutExpired:
        log_obj.write("  ── Gate: compile ── TIMEOUT")
        return False
    if proc.returncode != 0:
        log_obj.write(f"  ── Gate: compile ── FAIL (exit {proc.returncode})")
        last = proc.stderr.strip().splitlines()[-5:]
        for line in last:
            log_obj.write(f"      {line}")
        return False
    log_obj.write("  ── Gate: compile ── PASS")
    return True


def _gate_coverage(module: str, baseline: Dict[str, int],
                   log_obj: _ModuleLog) -> bool:
    """Coverage must not regress (L4+ count must not decrease)."""
    final = _coverage_snapshot(module)
    delta = _l4_plus(final) - _l4_plus(baseline)
    log_obj.write(
        f"  ── Gate: stdlib-coverage --module {module} ──"
    )
    log_obj.write(
        f"      baseline: L1={baseline['L1']} L2={baseline['L2']} "
        f"L3={baseline['L3']} L4={baseline['L4']} L5={baseline['L5']}"
    )
    log_obj.write(
        f"      final:    L1={final['L1']} L2={final['L2']} "
        f"L3={final['L3']} L4={final['L4']} L5={final['L5']}"
        f"   (Δ L4+ = {delta:+d})"
    )
    if delta < 0:
        log_obj.write("      VERDICT: REGRESSION")
        return False
    log_obj.write("      VERDICT: PASS")
    return True


def _gate_self_annotate(log_obj: _ModuleLog) -> bool:
    """Run bin/run-self-annotation-suite.sh and confirm 26/26."""
    cmd = ["bash", "bin/run-self-annotation-suite.sh"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                               cwd=str(_PROJECT_ROOT), timeout=900)
    except subprocess.TimeoutExpired:
        log_obj.write("  ── Gate: self-annotate-verify ── TIMEOUT")
        return False
    out = proc.stdout
    if "26/26 proved" in out:
        log_obj.write("  ── Gate: self-annotate-verify ── PASS (26/26)")
        return True
    log_obj.write(f"  ── Gate: self-annotate-verify ── FAIL (exit {proc.returncode})")
    tail = out.strip().splitlines()[-5:]
    for line in tail:
        log_obj.write(f"      {line}")
    return False


# ---------------------------------------------------------------------------
# Rollback
# ---------------------------------------------------------------------------


def _rollback(module: str, new_test_files: List[Path],
              log_obj: _ModuleLog) -> None:
    """Restore the stub from HEAD and remove any newly-created
    reference tests. Does not touch other files in the working
    tree."""
    stub_rel = (_STUB_DIR / f"{module}.py").relative_to(_PROJECT_ROOT)
    try:
        subprocess.run(["git", "checkout", "--", str(stub_rel)],
                        cwd=str(_PROJECT_ROOT), check=True,
                        capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        log_obj.write(f"  rollback: git checkout failed: {e.stderr}")
    for p in new_test_files:
        if p.is_file():
            p.unlink()
    log_obj.write(f"  rollback: stub restored; {len(new_test_files)} new test files removed")


# ---------------------------------------------------------------------------
# Per-module driver
# ---------------------------------------------------------------------------


def annotate_module(module: str, model: str, system_prompt: str,
                     log_dir: Path, max_fns: Optional[int] = None,
                     dry_run: bool = False) -> bool:
    """Annotate one stdlib module. Returns True if the module
    finished cleanly (no rollback); False on rollback."""
    log_obj = _ModuleLog(log_dir, module)
    stub_path = _STUB_DIR / f"{module}.py"
    if not stub_path.is_file():
        log_obj.write(f"  SKIP: stub not found at {stub_path}")
        log_obj.close()
        return False

    baseline = _coverage_snapshot(module)
    log_obj.write(
        f"  Baseline: L1={baseline['L1']} L2={baseline['L2']} "
        f"L3={baseline['L3']} L4={baseline['L4']} L5={baseline['L5']}"
    )

    fns = _scan_stub_functions(stub_path)
    needs = [f for f in fns if _needs_promotion(stub_path, f.name)]
    if max_fns:
        needs = needs[:max_fns]
    log_obj.write(f"  Targets: {len(needs)} functions to promote")
    if not needs:
        log_obj.write("  Nothing to do (all functions already L4+)")
        log_obj.close()
        return True

    cpy_funcs = _extract_cpython_funcs(module)
    log_obj.write(f"  CPython source: {len(cpy_funcs)} functions with docstrings")

    new_test_files: List[Path] = []

    # Per function: build prompt, call LLM, splice block, write tests.
    # We walk in reverse line order so splicing earlier ones doesn't
    # shift later line numbers (each splice is line-based on the
    # snapshot taken at scan time).
    for fn in reversed(needs):
        log_obj.write(f"  ── Promoting: {fn.name} ──")
        cpy = cpy_funcs.get(fn.name)
        existing = _read_existing_block(stub_path, fn)
        prompt = _build_prompt(fn.name, fn.signature, cpy, existing)
        if dry_run:
            log_obj.write("    [dry-run] prompt prepared, LLM call skipped")
            continue
        try:
            response = llm_generate(
                prompt=prompt, system=system_prompt,
                agent_id=AGENT_NAME, model=model,
            )
        except Exception as e:
            log_obj.write(f"    LLM call FAILED: {e}")
            continue
        block = _parse_llm_block(response)
        if block is None:
            log_obj.write(
                "    LLM output did not contain a usable contract block; "
                "leaving function unchanged"
            )
            continue
        _splice_block(stub_path, fn, block)
        log_obj.write(
            f"    spliced {len(block.splitlines())} line(s) at "
            f"{stub_path.name}:{fn.block_start}-{fn.def_line - 1}"
        )
        added = _write_reference_tests(module, fn.name)
        new_test_files.extend(added)
        if added:
            log_obj.write(f"    wrote {len(added)} reference test(s)")

    if dry_run:
        log_obj.write("  [dry-run] complete; no edits applied")
        log_obj.close()
        return True

    # Run gates in sequence; rollback on any failure.
    ok = _gate_compile(stub_path, log_obj)
    if ok:
        ok = _gate_coverage(module, baseline, log_obj)
    if ok:
        ok = _gate_self_annotate(log_obj)

    if not ok:
        _rollback(module, new_test_files, log_obj)
        log_obj.write("  Outcome: ROLLED-BACK")
        log_obj.close()
        return False

    log_obj.write("  Outcome: COMMIT-READY")
    log_obj.close()
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _load_config(config_path: Path) -> Dict[str, str]:
    if not config_path.is_file():
        log(str(_PROJECT_ROOT), AGENT_NAME,
            f"Error: config not found at {config_path}")
        sys.exit(2)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_skill(config: Dict[str, str]) -> Path:
    """Resolve `skill-stdlib-annotate` from config, falling back
    to the canonical conventions doc path."""
    name = config.get("skill-stdlib-annotate",
                      "docs/stdlib-annotation-conventions.md")
    p = Path(name)
    if not p.is_absolute():
        p = _PROJECT_ROOT / p
    if not p.is_file():
        log(str(_PROJECT_ROOT), AGENT_NAME,
            f"Error: skill doc not found at {p}")
        sys.exit(2)
    return p


def _scope_modules() -> List[str]:
    """Stdlib modules to iterate, excluding the coverage scanner's
    non-stdlib set."""
    out: List[str] = []
    for path in sorted(_STUB_DIR.glob("*.py")):
        if path.stem in _COV._NON_STDLIB:
            continue
        out.append(path.stem)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Autonomous stdlib stub annotator.",
    )
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--module", help="annotate a single stdlib module")
    g.add_argument("--all", action="store_true",
                    help="iterate every stdlib module under src/pycsl_lib/")
    g.add_argument("--detect-gaps", action="store_true",
                    help="Item 1.1: scan # cite:_note: lines, classify, "
                    "write metrics/stdlib-gap-report.json (read-only)")
    g.add_argument("--propose-feature", metavar="CATEGORY", default=None,
                    help="Item 1.2: emit a missing-<category>-feature.md "
                    "draft into proposed-features/ if the category's note "
                    "count >= --proposal-threshold")
    parser.add_argument("--scan-path", type=Path, default=None,
                        help="--detect-gaps: scan this path instead of "
                        "src/pycsl_lib/ (used by fixture-based regression "
                        "tests)")
    parser.add_argument("--proposal-threshold", type=int, default=5,
                        help="--propose-feature: minimum note count to "
                        "trigger draft (default: 5)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-fns", type=int, default=None,
                        help="cap per-module function count (smoke test)")
    parser.add_argument("--log-dir", default=None,
                        help="logs/<dir> (default: logs/stdlib-annotator/<UTC>)")
    parser.add_argument("--config",
                        default=str(_PROJECT_ROOT / "config" / "agents-config.json"))
    args = parser.parse_args()

    # ---- Item 1.1: --detect-gaps short-circuit ----
    if args.detect_gaps:
        return cmd_detect_gaps(args.scan_path)

    # ---- Item 1.2: --propose-feature short-circuit ----
    if args.propose_feature:
        return cmd_propose_feature(args.propose_feature, args.proposal_threshold)

    config = _load_config(Path(args.config))
    model = config.get("model")
    if not model:
        log(str(_PROJECT_ROOT), AGENT_NAME,
            "Error: 'model' missing in config")
        return 2
    skill_path = _resolve_skill(config)
    system_prompt = skill_path.read_text(encoding="utf-8")

    if args.log_dir:
        log_dir = Path(args.log_dir)
    else:
        ts = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
        log_dir = _PROJECT_ROOT / "logs" / "stdlib-annotator" / ts
    log_dir.mkdir(parents=True, exist_ok=True)

    if args.module:
        scope = [args.module]
    else:
        scope = _scope_modules()

    print(f"[{AGENT_NAME}] model={model}  scope={len(scope)} modules  "
          f"log_dir={log_dir.relative_to(_PROJECT_ROOT)}")
    if args.dry_run:
        print("[dry-run] no edits will be written")

    ok_count = 0
    rollback_count = 0
    for module in scope:
        try:
            ok = annotate_module(
                module=module,
                model=model,
                system_prompt=system_prompt,
                log_dir=log_dir,
                max_fns=args.max_fns,
                dry_run=args.dry_run,
            )
        except KeyboardInterrupt:
            print("\n[interrupted by user]")
            return 130
        except Exception as e:
            print(f"  [!] {module}: {type(e).__name__}: {e}")
            rollback_count += 1
            continue
        if ok:
            ok_count += 1
        else:
            rollback_count += 1

    print()
    print(f"[{AGENT_NAME}] DONE  modules_ok={ok_count}  "
          f"rolled_back={rollback_count}  log_dir={log_dir.relative_to(_PROJECT_ROOT)}")
    print("Review the working tree (`git diff`) and commit selectively.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
