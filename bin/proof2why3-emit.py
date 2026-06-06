#!/usr/bin/env python3
"""Emit `_AXIOM_REGISTRY` fragments from cross-checked IR.

Per todo-saturday.md Item 3. Given a Python file with
`#@ proof rocq/lean` citations, runs the same Rocq + Lean extraction
that `crosscheck_ir` does, takes the canonical IR for each citation,
and emits a dict literal mapping qualnames → WhyML axiom bodies.

Usage:
    bin/proof2why3-emit.py <py_file>

Output (stdout) is a Python dict-literal fragment:

    # AUTO-GENERATED from <py_file>
    "Pycsl.Reference.Gcd.gcd_step":
        "forall v0 v1 : int. v0 >= 0 -> v1 >= 0 -> v1 > 0 -> "
        "gcd v0 v1 = gcd v1 (mod v0 v1)",

ready for inclusion in `src/pycsl/module6_whyml/preamble.py`'s
`_AXIOM_REGISTRY`. Citations whose canonical IR contains an
`Unsupported` leaf are emitted as a comment with the existing
registry entry preserved (the merge tool reads the AUTO-GENERATED
marker to decide what to splice).

Exit codes:
    0  — success; output went to stdout.
    1  — at least one citation produced an Unsupported IR.
    2  — argument or file error.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))
sys.path.insert(0, str(_REPO_ROOT / "src" / "pycsl"))

from proof2why3.crosscheck_ir import crosscheck_file_ir
from proof2why3.emit_why3 import contains_unsupported, ir_to_whyml_axiom_body


def _format_body_literal(body: str, indent: str = "        ") -> str:
    """Wrap a body string as a Python string literal, splitting long
    lines for readability. Each line ends with a trailing space so
    Python's implicit concatenation reassembles it correctly when
    pasted into `_AXIOM_REGISTRY`."""
    if len(body) <= 70:
        return f'"{body}"'
    # Split at `-> ` boundaries on long lines.
    pieces: List[str] = []
    remaining = body
    while len(remaining) > 70:
        # Prefer splitting after `-> ` near col 70.
        cut = remaining.rfind("-> ", 0, 70)
        if cut < 0:
            cut = remaining.rfind(" ", 0, 70)
        if cut < 0:
            break
        cut += 3 if remaining[cut:cut + 3] == "-> " else 1
        pieces.append(remaining[:cut])
        remaining = remaining[cut:]
    pieces.append(remaining)
    return "\n".join(f'{indent}"{p}"' for p in pieces).lstrip()


def emit_file(py_file: Path) -> Dict[str, str]:
    """Return a dict mapping qualname → emitted WhyML axiom body for
    every cross-checked citation in `py_file` that has an existing
    registry entry. Audit-anchor stubs (citations without a
    `_AXIOM_REGISTRY` body — decidable-equality declarations,
    pure type anchors, …) are deliberately skipped: they don't
    have an axiom-body shape and shouldn't be promoted to one.

    The canonical IR is derived from the **prover** side (Rocq
    first, Lean fallback) — never from the registry itself.
    Deriving from the registry would defeat the merge tool's
    purpose: it would copy the registry to the registry. When
    only the registry has a canon (no prover evidence), we skip:
    there's nothing to regenerate against.

    Within the registered subset, citations whose canonical IR
    contains an `Unsupported` leaf are skipped too — the parser
    couldn't represent the term, so emitting would yield garbage."""
    results = crosscheck_file_ir(py_file)
    out: Dict[str, str] = {}
    for r in results:
        if not r.registry_raw:
            continue  # Audit-anchor stub.
        canon = r.rocq_canon or r.lean_canon
        if canon is None or contains_unsupported(canon):
            continue
        out[r.qualname] = ir_to_whyml_axiom_body(canon)
    return out


def _check_registry_roundtrip() -> int:
    """Verify every existing `_AXIOM_REGISTRY` entry round-trips:
    parse → canonicalize → emit → parse → canonicalize must produce
    the same canonical Term as the original. Bound names alpha-rename
    to v0/v1/… but the canonical equivalence class is preserved.

    Returns 0 on success, 1 on any mismatch."""
    from proof2why3.parser import parse_type_expr
    from proof2why3.canonical import canonicalize
    from proof2why3.crosscheck_ir import _load_axiom_registry, _preprocess_whyml

    registry = _load_axiom_registry()
    if not registry:
        print("error: _AXIOM_REGISTRY is empty", file=sys.stderr)
        return 1
    n_pass = 0
    n_fail = 0
    for qn, body in sorted(registry.items()):
        canon1 = canonicalize(parse_type_expr(_preprocess_whyml(body)))
        emitted = ir_to_whyml_axiom_body(canon1)
        canon2 = canonicalize(parse_type_expr(_preprocess_whyml(emitted)))
        if canon1 == canon2:
            print(f"  ✓ {qn}")
            n_pass += 1
        else:
            print(f"  ✗ {qn}")
            print(f"      original : {body}")
            print(f"      emitted  : {emitted}")
            print(f"      canon1   : {canon1.pp()}")
            print(f"      canon2   : {canon2.pp()}")
            n_fail += 1
    print(f"=== proof2why3 emit round-trip: {n_pass} PASS / {n_fail} FAIL ===")
    return 0 if n_fail == 0 else 1


def main(argv: List[str]) -> int:
    if len(argv) == 1 and argv[0] == "--check":
        return _check_registry_roundtrip()
    if len(argv) != 1:
        print("usage: proof2why3-emit.py <py_file>", file=sys.stderr)
        print("       proof2why3-emit.py --check", file=sys.stderr)
        return 2
    py_file = Path(argv[0]).resolve()
    if not py_file.is_file():
        print(f"error: not a file: {py_file}", file=sys.stderr)
        return 2

    entries = emit_file(py_file)
    if not entries:
        print(f"# {py_file}: no emittable citations", file=sys.stderr)
        return 0

    print(f"# AUTO-GENERATED from {py_file.relative_to(_REPO_ROOT)}")
    for qn, body in sorted(entries.items()):
        literal = _format_body_literal(body)
        if "\n" in literal:
            print(f'    "{qn}":')
            print(f"        {literal}")
            print("    ,")
        else:
            print(f'    "{qn}": {literal},')
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
