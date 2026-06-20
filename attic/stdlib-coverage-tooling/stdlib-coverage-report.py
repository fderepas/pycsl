#!/usr/bin/env python3
"""Classify stdlib stub functions by annotation depth.

Phase 0 of the fully-annotated-stdlib strategy (see
`.claude/plans/parsed-booping-ember.md`). Walks
`src/pycsl_lib/*.py`, classifies every top-level function and
class method by annotation depth, and emits a coverage report.

Annotation depth levels:

- **L1 typed**: function present, no `#@ \\trusted` directive
  immediately preceding.
- **L2 trusted**: `#@ \\trusted` present but no semantic
  `requires` / `ensures` (or only the placeholder
  `ensures \\result >= 0`).
- **L3 partial**: `#@ \\trusted` plus at least one semantic
  `requires` OR `ensures` (a clause that is non-trivially
  derived from the function's documentation).
- **L4 full**: `#@ \\trusted` plus at least one semantic
  `requires` AND at least one semantic `ensures`.
- **L5 tested**: L4 plus a reference test exists at
  `test-suite/corpus/python-reference/stdlib/<module>/`
  whose filename contains the function name.

The placeholder `#@ ensures \\result >= 0` (or `== 0`) on
otherwise unannotated stubs is treated as L2, not L3 — it's
a type-shape assertion, not a semantic contract.

Usage:
    bin/stdlib-coverage-report.py              # full report
    bin/stdlib-coverage-report.py --module math   # one module
    bin/stdlib-coverage-report.py --json       # machine output
    bin/stdlib-coverage-report.py --gen-doc    # regenerate
                                               # docs/stdlib-coverage.md

Exit codes:
    0 — success.
    2 — argument error.
"""
from __future__ import annotations

import json as _json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

_REPO_ROOT = Path(__file__).resolve().parent.parent
_STUB_DIR = _REPO_ROOT / "src" / "pycsl_lib"
_TEST_DIR = _REPO_ROOT / "test-suite" / "corpus" / "python-reference" / "stdlib"
_DOC_PATH = _REPO_ROOT / "docs" / "stdlib-coverage.md"

# Stub files that are PyCSL internal mocks, not stdlib modules.
# Excluded from coverage tallies (they aren't part of the
# "annotate Python stdlib" effort).
_NON_STDLIB = {
    "Module1_Ingestor", "Module2_Parser", "Module3_Weaver",
    "Module4_SemanticAnalyzer", "Module5_IREmitter",
    "Module6_WhyMLTranspiler",
    "__future__",
    # Third-party tools, separate strategy:
    "jsonschema", "lark", "libcst", "mcp", "numpy",
}


# ---------------------------------------------------------------------------
# Annotation block parsing
# ---------------------------------------------------------------------------


# Match the placeholder-only `ensures` shapes that don't carry
# semantic content — pure type-shape assertions on the mock
# return value.
_PLACEHOLDER_ENSURES = re.compile(
    r"^#@\s*ensures\s+\\result\s*(==|>=|<=)\s*-?\d+\s*$"
)
# Match the placeholder-only `requires True`.
_PLACEHOLDER_REQUIRES = re.compile(
    r"^#@\s*requires\s+True\s*$"
)


@dataclass
class _Block:
    """The `#@` directives directly preceding a function or
    method definition. Lines are stored verbatim, stripped of
    trailing whitespace."""
    lines: List[str] = field(default_factory=list)

    @property
    def has_trusted(self) -> bool:
        return any(re.match(r"^#@\s*\\trusted\b", line) for line in self.lines)

    @property
    def has_cite(self) -> bool:
        """A `# cite: <URL>` marker (regular Python comment, not
        a `#@` directive) indicates the contract was deliberately
        analyzed against the official Python docs. Used as the
        "reviewed" signal for L4 promotion when the function has
        no semantic precondition (some functions accept any
        input of the declared type — `math.ceil` is the
        canonical example).

        Regular Python comment is used rather than a `#@`
        directive because the PyCSL parser's grammar restricts
        the directive set and adding `\\cite` would require a
        grammar extension. The scanner reads raw file lines so
        a Python comment is sufficient."""
        return any(re.match(r"^#\s*cite:\s*https?://", line)
                   for line in self.lines)

    @property
    def semantic_requires(self) -> int:
        n = 0
        for line in self.lines:
            if not re.match(r"^#@\s*requires\b", line):
                continue
            if _PLACEHOLDER_REQUIRES.match(line):
                continue
            n += 1
        return n

    @property
    def semantic_ensures(self) -> int:
        n = 0
        for line in self.lines:
            if not re.match(r"^#@\s*ensures\b", line):
                continue
            if _PLACEHOLDER_ENSURES.match(line):
                continue
            n += 1
        return n


def _extract_function_blocks(source: str) -> List[Tuple[str, _Block]]:
    """Walk `source` line by line. For each `def <name>(...)` or
    `async def <name>(...)`, return its name and the contiguous
    `#@` comment block immediately preceding it.

    Skips definitions whose name starts with `_` (private) — the
    coverage strategy targets the public surface only."""
    out: List[Tuple[str, _Block]] = []
    lines = source.splitlines()
    n = len(lines)
    i = 0
    while i < n:
        line = lines[i].strip()
        m = re.match(r"^(?:async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", line)
        if not m:
            i += 1
            continue
        name = m.group(1)
        # Walk backwards over the contiguous block of `#@` lines.
        block = _Block()
        j = i - 1
        while j >= 0:
            stripped = lines[j].strip()
            if stripped.startswith("#@"):
                block.lines.append(stripped)
                j -= 1
            elif re.match(r"^#\s*cite:\s*https?://", stripped):
                # Cite comments are part of the contract block
                # even though they aren't `#@` directives — they
                # signal "deliberately reviewed against the docs"
                # for L4 promotion.
                block.lines.append(stripped)
                j -= 1
            elif not stripped:
                # Allow blank lines between def and block? PyCSL
                # convention puts the block contiguous; break.
                break
            else:
                break
        block.lines.reverse()
        if not name.startswith("_"):
            out.append((name, block))
        i += 1
    return out


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


@dataclass
class _FnReport:
    name: str
    level: str           # "L1" .. "L5"
    tested: bool = False


@dataclass
class _ModuleReport:
    module: str
    total: int = 0
    counts: Dict[str, int] = field(default_factory=lambda: {
        "L1": 0, "L2": 0, "L3": 0, "L4": 0, "L5": 0,
    })
    fns: List[_FnReport] = field(default_factory=list)

    @property
    def coverage_pct(self) -> float:
        """Percentage of functions at L4 or higher."""
        if self.total == 0:
            return 0.0
        return 100.0 * (self.counts["L4"] + self.counts["L5"]) / self.total


def _module_test_index(module: str) -> Set[str]:
    """Return the set of test-file basenames under
    `test-suite/corpus/python-reference/stdlib/<module>/`.
    Used by L5 detection — a function is L5 iff its name appears
    as a substring of any test filename in this set."""
    d = _TEST_DIR / module
    if not d.is_dir():
        return set()
    return {p.name for p in d.glob("*.py")}


def _classify_block(block: _Block) -> str:
    """Map a `#@` block to its annotation level (L1..L4).
    L5 (tested) is determined separately at the module scan
    level, since it depends on reference test existence.

    L4 requires at least one semantic `ensures` AND one of:
      (a) at least one semantic `requires`, OR
      (b) a `#@ \\cite` marker (signals deliberate review
          against the docs — some Python functions accept any
          input of the declared type, so "no precondition" is
          itself the reviewed answer)."""
    if not block.has_trusted:
        return "L1"
    has_req = block.semantic_requires > 0
    has_ens = block.semantic_ensures > 0
    if has_ens and (has_req or block.has_cite):
        return "L4"
    if has_req or has_ens:
        return "L3"
    return "L2"


def _analyze_module(stub_path: Path) -> _ModuleReport:
    module = stub_path.stem
    report = _ModuleReport(module=module)
    source = stub_path.read_text()
    test_files = _module_test_index(module)
    for name, block in _extract_function_blocks(source):
        level = _classify_block(block)
        tested = (level == "L4") and any(name in tf for tf in test_files)
        if tested:
            level = "L5"
        report.fns.append(_FnReport(name=name, level=level, tested=tested))
        report.counts[level] += 1
        report.total += 1
    return report


def _all_modules() -> List[_ModuleReport]:
    """Analyze every stdlib stub under `src/pycsl_lib/`,
    excluding internal PyCSL mocks and third-party stubs."""
    out: List[_ModuleReport] = []
    for path in sorted(_STUB_DIR.glob("*.py")):
        if path.stem in _NON_STDLIB:
            continue
        out.append(_analyze_module(path))
    return out


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _print_human(reports: List[_ModuleReport]) -> None:
    total = sum(r.total for r in reports)
    totals = {k: sum(r.counts[k] for r in reports) for k in
              ("L1", "L2", "L3", "L4", "L5")}
    overall_pct = 0.0
    if total:
        overall_pct = 100.0 * (totals["L4"] + totals["L5"]) / total
    print("=== Stdlib stub coverage report ===")
    print(f"Stub dir: {_STUB_DIR.relative_to(_REPO_ROOT)}")
    print(f"Modules:  {len(reports)}    Functions: {total}")
    print()
    header = f"| {'Module':<14} | {'Total':>5} | {'L1':>3} | "
    header += f"{'L2':>3} | {'L3':>3} | {'L4':>3} | {'L5':>3} | "
    header += f"{'L4+%':>5} |"
    print(header)
    print("|" + "-" * (len(header) - 2) + "|")
    for r in reports:
        line = f"| {r.module:<14} | {r.total:>5} | "
        for k in ("L1", "L2", "L3", "L4", "L5"):
            line += f"{r.counts[k]:>3} | "
        line += f"{r.coverage_pct:>4.1f}% |"
        print(line)
    print("|" + "-" * (len(header) - 2) + "|")
    foot = f"| {'TOTAL':<14} | {total:>5} | "
    for k in ("L1", "L2", "L3", "L4", "L5"):
        foot += f"{totals[k]:>3} | "
    foot += f"{overall_pct:>4.1f}% |"
    print(foot)


def _print_json(reports: List[_ModuleReport]) -> None:
    total = sum(r.total for r in reports)
    totals = {k: sum(r.counts[k] for r in reports) for k in
              ("L1", "L2", "L3", "L4", "L5")}
    overall_pct = 100.0 * (totals["L4"] + totals["L5"]) / total if total else 0.0
    obj = {
        "stub_dir": str(_STUB_DIR.relative_to(_REPO_ROOT)),
        "total_functions": total,
        "totals": totals,
        "overall_l4_plus_pct": round(overall_pct, 2),
        "modules": [
            {
                "module": r.module,
                "total": r.total,
                "counts": r.counts,
                "coverage_pct": round(r.coverage_pct, 2),
                "fns": [{"name": f.name, "level": f.level} for f in r.fns],
            }
            for r in reports
        ],
    }
    print(_json.dumps(obj, indent=2))


def _gen_doc(reports: List[_ModuleReport]) -> str:
    """Render `docs/stdlib-coverage.md` content. Mechanically
    regenerated — do not edit by hand."""
    total = sum(r.total for r in reports)
    totals = {k: sum(r.counts[k] for r in reports) for k in
              ("L1", "L2", "L3", "L4", "L5")}
    overall_pct = 100.0 * (totals["L4"] + totals["L5"]) / total if total else 0.0
    lines: List[str] = []
    lines.append("# Python stdlib stub coverage")
    lines.append("")
    lines.append("_Auto-generated by `bin/stdlib-coverage-report.py --gen-doc`._")
    lines.append("_Do not edit by hand. Run `make stdlib-coverage` to regenerate._")
    lines.append("")
    lines.append("## Annotation depth levels")
    lines.append("")
    lines.append("- **L1 typed** — function present, no `#@ \\trusted`.")
    lines.append("- **L2 trusted** — `#@ \\trusted` only (or with placeholder")
    lines.append("  `ensures \\result >= 0` / `requires True` / similar).")
    lines.append("- **L3 partial** — `#@ \\trusted` + at least one semantic")
    lines.append("  `requires` OR `ensures` derived from the Python docs.")
    lines.append("- **L4 full** — `#@ \\trusted` + at least one semantic")
    lines.append("  `ensures`, AND either (a) at least one semantic")
    lines.append("  `requires` OR (b) a `#@ \\cite` marker (deliberate")
    lines.append("  review against the docs).")
    lines.append("- **L5 tested** — L4 + a reference test under")
    lines.append("  `test-suite/corpus/python-reference/stdlib/<module>/`")
    lines.append("  whose filename contains the function name.")
    lines.append("")
    lines.append(f"**Overall:** {total} functions across {len(reports)} modules.")
    lines.append(f"**L4+ coverage:** {overall_pct:.1f}%.")
    lines.append("")
    lines.append("## Per-module coverage")
    lines.append("")
    lines.append("| Module | Total | L1 | L2 | L3 | L4 | L5 | L4+ % |")
    lines.append("|--------|------:|---:|---:|---:|---:|---:|------:|")
    for r in reports:
        lines.append(
            f"| `{r.module}` | {r.total} | "
            f"{r.counts['L1']} | {r.counts['L2']} | {r.counts['L3']} | "
            f"{r.counts['L4']} | {r.counts['L5']} | "
            f"{r.coverage_pct:.1f}% |"
        )
    lines.append(
        f"| **TOTAL** | **{total}** | "
        f"**{totals['L1']}** | **{totals['L2']}** | **{totals['L3']}** | "
        f"**{totals['L4']}** | **{totals['L5']}** | "
        f"**{overall_pct:.1f}%** |"
    )
    lines.append("")
    lines.append("## L4/L5 functions (the annotated set)")
    lines.append("")
    has_any = False
    for r in reports:
        annotated = [f for f in r.fns if f.level in ("L4", "L5")]
        if not annotated:
            continue
        has_any = True
        lines.append(f"### `{r.module}`")
        lines.append("")
        for f in annotated:
            mark = "✓" if f.level == "L5" else "·"
            lines.append(f"- {mark} `{f.name}` ({f.level})")
        lines.append("")
    if not has_any:
        lines.append("_(No functions at L4 or higher yet.)_")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("See `.claude/plans/parsed-booping-ember.md` for the")
    lines.append("multi-quarter annotation strategy.")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: List[str]) -> int:
    want_json = False
    want_gen = False
    module_filter: Optional[str] = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--json":
            want_json = True
        elif a == "--gen-doc":
            want_gen = True
        elif a == "--module":
            i += 1
            if i >= len(argv):
                print("error: --module requires an argument", file=sys.stderr)
                return 2
            module_filter = argv[i]
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            print(f"error: unknown argument: {a}", file=sys.stderr)
            return 2
        i += 1

    if module_filter:
        path = _STUB_DIR / f"{module_filter}.py"
        if not path.is_file():
            print(f"error: stub not found: {path}", file=sys.stderr)
            return 2
        reports = [_analyze_module(path)]
    else:
        reports = _all_modules()

    if want_gen:
        _DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
        _DOC_PATH.write_text(_gen_doc(reports))
        print(f"=== Wrote {_DOC_PATH.relative_to(_REPO_ROOT)} ===")
        return 0

    if want_json:
        _print_json(reports)
    else:
        _print_human(reports)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
