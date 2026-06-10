#!/usr/bin/env python3
"""Core-only conformance runner — refactor.md Phase E, corpus (1): golden-IR → expected-WhyML.

Proves the language-agnostic CORE re-derives byte-identical WhyML from a golden (resolved)
IR with NO front-end (Modules 1-5) involved. It imports only the core surface — ``ir_schema``,
``core_ir_semantic``, ``Module6_WhyMLTranspiler`` — and asserts at import time that no
front-end module leaked into ``sys.modules`` (that would invalidate the "core alone" claim).

For each ``<corpus-dir>/NNNN.ir.json`` (a golden, fully-resolved IR) paired with
``NNNN.expected.mlw``: load the golden, run the core's ``validate_ir`` +
``run_ir_semantic_checks``, transpile via Module 6, and byte-diff against the expected
WhyML. Exit non-zero on any mismatch or any front-end import.

Usage:  core-only-conformance.py [corpus-dir]
        (default corpus-dir: test-suite/corpus/conformance/core)
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "pycsl"))

from ir_schema import validate_ir                       # noqa: E402
from core_ir_semantic import run_ir_semantic_checks     # noqa: E402
from Module6_WhyMLTranspiler import Module6_WhyMLTranspiler  # noqa: E402

# The whole point of the seam: importing the core must not pull in any front-end module.
_FRONTEND_PREFIXES = ("Module1", "Module2", "Module3", "Module4", "Module5", "pure_ast")
_leaked = sorted(m for m in sys.modules if m.startswith(_FRONTEND_PREFIXES))
if _leaked:
    print(f"[!] core-only violation: front-end modules loaded by the core: {_leaked}")
    sys.exit(2)


def run(corpus_dir: str) -> int:
    goldens = sorted(glob.glob(os.path.join(corpus_dir, "*.ir.json")))
    if not goldens:
        print(f"[!] no *.ir.json golden inputs found in {corpus_dir}")
        return 2
    ok = 0
    fail = 0
    for g in goldens:
        base = g[: -len(".ir.json")]
        name = os.path.basename(base)
        expected_path = base + ".expected.mlw"
        if not os.path.exists(expected_path):
            print(f"  {name}: MISSING expected .mlw")
            fail += 1
            continue
        with open(g) as f:
            wire = f.read()
        ir = json.loads(wire)
        validate_ir(ir)
        run_ir_semantic_checks(ir)
        mlw = Module6_WhyMLTranspiler(wire).transpile()
        with open(expected_path) as f:
            expected = f.read()
        if mlw == expected:
            ok += 1
        else:
            fail += 1
            print(f"  {name}: MLW MISMATCH ({len(mlw)}B core-only vs {len(expected)}B expected)")
    print(f"[{'+' if not fail else '!'}] core-only conformance: {ok} OK / {fail} MISMATCH "
          f"({len(goldens)} goldens) — front-end NOT imported")
    return 1 if fail else 0


if __name__ == "__main__":
    cd = sys.argv[1] if len(sys.argv) > 1 else "test-suite/corpus/conformance/core"
    sys.exit(run(cd))
