#!/usr/bin/env python3
"""Merge auto-generated `_AXIOM_REGISTRY` entries back into
`src/pycsl/module6_whyml/preamble.py`.

Per todo-saturday.md Item 3 (Day-2/3 stretch). Walks every annotated
Python file (`#@ proof rocq/lean …` citations), calls
`bin/proof2why3-emit.py:emit_file` per file, and reconciles against
the current registry.

Design rule — **drift-aware merge** (not blind overwrite):

  * **New qualname** (in any annotated file's emit but not in the
    registry) → add with the auto-generated v0/v1 body.
  * **Existing qualname, canonical forms agree** → keep the
    existing hand-curated body. Preserves readable variable names.
  * **Existing qualname, canonical forms differ** → replace with
    the auto-generated body. Drift detection: signals a divergence
    between proof side and registry side, escalated by the rewrite.
  * **Existing qualname, no emit available** → keep the existing
    body. Defensive: audit-anchor stubs and unparsable proofs
    shouldn't lose their hand-curated entries.

Usage:
    bin/proof2why3-merge-registry.py             # dry-run: report deltas
    bin/proof2why3-merge-registry.py --write     # rewrite preamble.py

Exit codes:
    0  — no changes needed (or write succeeded with deltas reported).
    1  — drift detected (dry-run); rerun with --write to apply.
    2  — argument error.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))
sys.path.insert(0, str(_REPO_ROOT / "src" / "pycsl"))

# Import after sys.path mutation so the proof2why3 package resolves.
from proof2why3.canonical import canonicalize  # noqa: E402
from proof2why3.crosscheck_ir import (  # noqa: E402
    _load_axiom_registry, _preprocess_whyml,
)
from proof2why3.parser import parse_type_expr  # noqa: E402

sys.path.insert(0, str(_REPO_ROOT / "bin"))
# proof2why3-emit.py is a script-name with dashes; use importlib.
import importlib.util  # noqa: E402

_EMIT_PATH = _REPO_ROOT / "bin" / "proof2why3-emit.py"
_spec = importlib.util.spec_from_file_location("proof2why3_emit", _EMIT_PATH)
proof2why3_emit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(proof2why3_emit)
emit_file = proof2why3_emit.emit_file  # type: ignore[attr-defined]


_PREAMBLE_PATH = _REPO_ROOT / "src" / "pycsl" / "module6_whyml" / "preamble.py"


# ---------------------------------------------------------------------------
# Source discovery
# ---------------------------------------------------------------------------


_CANDIDATE_GLOBS = [
    "src/self-annotate/src/*.py",
    "src/self-annotate/src/module6_whyml/*.py",
    "test-suite/corpus/pycsl-reference/*.py",
]


def _annotated_files() -> List[Path]:
    """All Python files in the corpus with at least one `#@ proof`
    citation. Same scan that `bin/check-proof-crosscheck.sh` uses."""
    out: List[Path] = []
    for glob in _CANDIDATE_GLOBS:
        for p in sorted(_REPO_ROOT.glob(glob)):
            if not p.is_file():
                continue
            try:
                if "#@ proof " in p.read_text():
                    out.append(p)
            except (OSError, UnicodeDecodeError):
                pass
    return out


# ---------------------------------------------------------------------------
# Drift detection
# ---------------------------------------------------------------------------


def _canon_of(body: str):
    """Canonical-form Term for a registry body string. Returns None
    if the parser couldn't represent it."""
    try:
        return canonicalize(parse_type_expr(_preprocess_whyml(body)))
    except Exception:
        return None


def _collect_emitted() -> Dict[str, str]:
    """Union of `emit_file` outputs across every annotated file.
    Conflicts (same qualname emitted from multiple files with
    different canonical forms) raise — that's a corpus-level
    inconsistency that the merge tool shouldn't paper over."""
    out: Dict[str, str] = {}
    seen_canon: Dict[str, object] = {}
    for f in _annotated_files():
        fragments = emit_file(f)
        for qn, body in fragments.items():
            c = _canon_of(body)
            if qn in seen_canon and seen_canon[qn] != c:
                raise SystemExit(
                    f"error: qualname {qn} emitted with conflicting "
                    f"canonical forms across multiple files; resolve "
                    f"manually before re-running"
                )
            seen_canon[qn] = c
            out[qn] = body
    return out


def _classify(existing: Dict[str, str],
              emitted: Dict[str, str]) -> Tuple[
        List[str], List[Tuple[str, str, str]], List[str], List[str]]:
    """Partition qualnames into four buckets:

      * `added`    — in `emitted`, not in `existing`.
      * `replaced` — in both; canonical forms differ.
                     Each entry is (qn, old_body, new_body).
      * `kept`     — in both; canonical forms agree.
      * `orphan`   — in `existing`, not in `emitted` (no proof
                     evidence; we keep these, but report them)."""
    added: List[str] = []
    replaced: List[Tuple[str, str, str]] = []
    kept: List[str] = []
    orphan: List[str] = []
    for qn, new in sorted(emitted.items()):
        if qn not in existing:
            added.append(qn)
            continue
        old = existing[qn]
        if _canon_of(old) == _canon_of(new):
            kept.append(qn)
        else:
            replaced.append((qn, old, new))
    for qn in sorted(existing):
        if qn not in emitted:
            orphan.append(qn)
    return added, replaced, kept, orphan


# ---------------------------------------------------------------------------
# Rewriting preamble.py
# ---------------------------------------------------------------------------


def _find_registry_span(source: str) -> Tuple[int, int]:
    """Return the (start_line, end_line) of the `_AXIOM_REGISTRY:
    Dict[str, str] = { … }` AnnAssign statement. Lines are 1-based,
    inclusive."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.target.id == "_AXIOM_REGISTRY":
            return node.lineno, node.end_lineno
    raise RuntimeError("_AXIOM_REGISTRY definition not found in preamble.py")


def _escape_for_double_quoted(body: str) -> str:
    """Escape `body` for inclusion inside a Python double-quoted
    string literal. Only backslashes and double quotes need escaping
    here; WhyML axiom bodies contain neither newlines nor other
    control characters."""
    return body.replace("\\", "\\\\").replace('"', '\\"')


def _format_body_value(body: str, indent: str) -> str:
    """Format a body string for inclusion in the dict literal.
    Short bodies fit on a single line; long bodies use Python's
    implicit string concatenation across multiple indented lines.
    Backslashes are escaped so the resulting Python source parses
    without SyntaxWarning."""
    esc = _escape_for_double_quoted(body)
    if len(esc) <= 70:
        return f'"{esc}"'
    pieces: List[str] = []
    remaining = esc
    while len(remaining) > 70:
        cut = remaining.rfind("-> ", 0, 70)
        if cut < 0:
            cut = remaining.rfind(" ", 0, 70)
        if cut < 0:
            break
        cut += 3 if remaining[cut:cut + 3] == "-> " else 1
        pieces.append(remaining[:cut])
        remaining = remaining[cut:]
    pieces.append(remaining)
    return ("\n" + indent).join(f'"{p}"' for p in pieces)


def _render_registry(merged: Dict[str, str], indent: str = "    ") -> str:
    """Render the merged registry dict literal at the given indent
    level (matching the class-attribute indent in preamble.py)."""
    lines: List[str] = []
    lines.append(f"{indent}_AXIOM_REGISTRY: Dict[str, str] = {{")
    lines.append(f"{indent}    # ============================================================")
    lines.append(f"{indent}    # Generated/maintained by `make sync-axiom-registry`")
    lines.append(f"{indent}    # (bin/proof2why3-merge-registry.py). Entries that already")
    lines.append(f"{indent}    # match the cross-checked canonical form retain their")
    lines.append(f"{indent}    # hand-curated variable names; drifted entries are")
    lines.append(f"{indent}    # rewritten to the canonical v0/v1/… form. Cross-check")
    lines.append(f"{indent}    # gate at `make check-proof-crosscheck` enforces")
    lines.append(f"{indent}    # registry-vs-prover agreement.")
    lines.append(f"{indent}    # ============================================================")
    value_indent = indent + "        "
    for qn in sorted(merged):
        body = merged[qn]
        formatted = _format_body_value(body, value_indent)
        if "\n" in formatted:
            lines.append(f'{indent}    "{qn}":')
            lines.append(f'{value_indent}{formatted},')
        else:
            lines.append(f'{indent}    "{qn}":')
            lines.append(f'{value_indent}{formatted},')
    lines.append(f"{indent}}}")
    return "\n".join(lines)


def _splice_registry(source: str, rendered: str) -> str:
    """Replace the existing `_AXIOM_REGISTRY` AnnAssign with the
    rendered block. Preserves all surrounding content verbatim."""
    start, end = _find_registry_span(source)
    src_lines = source.split("\n")
    # The lineno is 1-based inclusive. Python's slicing is 0-based.
    before = src_lines[: start - 1]
    after = src_lines[end:]
    return "\n".join(before + rendered.split("\n") + after)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print_report(added: List[str],
                  replaced: List[Tuple[str, str, str]],
                  kept: List[str],
                  orphan: List[str]) -> None:
    print(f"=== proof2why3 merge-registry ===")
    print(f"  kept (already canonical):  {len(kept)}")
    print(f"  added (new from proofs):   {len(added)}")
    print(f"  replaced (drift fixed):    {len(replaced)}")
    print(f"  orphan (no proof source):  {len(orphan)}")
    if added:
        print()
        print("Added:")
        for qn in added:
            print(f"  + {qn}")
    if replaced:
        print()
        print("Replaced (drift):")
        for qn, old, new in replaced:
            print(f"  ~ {qn}")
            print(f"    old: {old!r}")
            print(f"    new: {new!r}")
    if orphan:
        print()
        print("Orphan (kept; not regenerated):")
        for qn in orphan:
            print(f"  · {qn}")


def main(argv: List[str]) -> int:
    write = False
    if len(argv) == 0:
        write = False
    elif len(argv) == 1 and argv[0] == "--write":
        write = True
    else:
        print("usage: proof2why3-merge-registry.py [--write]", file=sys.stderr)
        return 2

    existing = _load_axiom_registry()
    emitted = _collect_emitted()
    added, replaced, kept, orphan = _classify(existing, emitted)

    _print_report(added, replaced, kept, orphan)

    if not added and not replaced:
        print()
        print("=== No changes needed. ===")
        return 0

    # Build the merged dict: keep agreeing entries verbatim,
    # replace drifted ones, add new ones, keep orphans verbatim.
    merged: Dict[str, str] = {}
    for qn in kept:
        merged[qn] = existing[qn]
    for qn, _old, new in replaced:
        merged[qn] = new
    for qn in added:
        merged[qn] = emitted[qn]
    for qn in orphan:
        merged[qn] = existing[qn]

    rendered = _render_registry(merged)

    if not write:
        print()
        print("=== Dry-run. Rerun with --write to modify preamble.py. ===")
        return 1

    source = _PREAMBLE_PATH.read_text()
    updated = _splice_registry(source, rendered)
    _PREAMBLE_PATH.write_text(updated)
    print()
    print(f"=== Wrote {_PREAMBLE_PATH}. ===")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
