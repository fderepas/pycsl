#!/usr/bin/env python3
"""regen-ir-conformance-goldens.py — refresh the IR-conformance goldens (docs/ir.md §10).

Reconcile helper for reconcile-ir-conformance.md. Two phases, selected by arg:

  ir     — regenerate every core/NNNN.ir.json from pycsl-reference/NNNN.py via the
           front-end runner's OWN derive_resolved_ir (canonical json.dumps(indent=2)),
           so the output is byte-identical to what frontend-only-conformance re-derives.
  mlw    — regenerate every core/NNNN.expected.mlw from the (already refreshed) golden IR
           via the core-only path (validate_ir + run_ir_semantic_checks + Module6), the
           exact pipeline core-only-conformance byte-diffs against.

Run under PYTHONHASHSEED=0. Delete this script (or keep gated) after the reconcile commit.
"""
import os, sys, glob, importlib.util, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(ROOT, "test-suite", "corpus", "conformance", "core")
REF = os.path.join(ROOT, "test-suite", "corpus", "pycsl-reference")


def regen_ir():
    spec = importlib.util.spec_from_file_location(
        "feconf", os.path.join(ROOT, "bin", "frontend-only-conformance.py"))
    fe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fe)
    for g in sorted(glob.glob(os.path.join(CORE, "*.ir.json"))):
        name = os.path.basename(g)[: -len(".ir.json")]
        ir = fe.derive_resolved_ir(os.path.join(REF, f"{name}.py"))
        with open(g, "w") as f:
            f.write(ir)
        print("ir.json", name)


def regen_mlw():
    # core surface ONLY — mirror core-only-conformance.py's imports exactly.
    sys.path.insert(0, os.path.join(ROOT, "src", "pycsl"))
    from ir_schema import validate_ir
    from core_ir_semantic import run_ir_semantic_checks
    from Module6_WhyMLTranspiler import Module6_WhyMLTranspiler
    for g in sorted(glob.glob(os.path.join(CORE, "*.ir.json"))):
        base = g[: -len(".ir.json")]
        name = os.path.basename(base)
        wire = open(g).read()
        ir = json.loads(wire)
        validate_ir(ir)
        run_ir_semantic_checks(ir)
        mlw = Module6_WhyMLTranspiler(wire).transpile()
        with open(base + ".expected.mlw", "w") as f:
            f.write(mlw)
        print("expected.mlw", name)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "ir":
        regen_ir()
    elif mode == "mlw":
        regen_mlw()
    else:
        sys.exit("usage: regen-ir-conformance-goldens.py {ir|mlw}")
