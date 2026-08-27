#!/usr/bin/env python3
r"""check-mirror-field-parity.py — FIDELITY GATE for class-level FIELD annotations.

THE HOLE THIS CLOSES. `self-annotate-mirror-check.sh` compares FUNCTION and CLASS
signatures between `src/pycsl/` and `src/self-annotate/src/`, and
`check-self-annotate-mirror-sync.py` compares un-`\trusted` method BODIES. Neither looks at
a class's ANNOTATED FIELDS — so a dataclass field can carry a different type in the mirror
than in the live source indefinitely, with every existing gate green.

Measured 2026-08-27 (relaunch #4), the first time anyone looked: **91 of 335 compared fields had
drifted.** The dominant pattern was 84 CSL-AST fields that the live source retyped
`CSLNode` -> `'ExprIR'` for the Module5 construction build, while the mirror still said
`CSLNode`. Not unsound — the mirror was the WEAKER model, and `CSLNode` int-erases where
`'ExprIR'` carries a real `emit_ir` child — but it meant 84 fields were modelled as opaque
integers in the verified artifact while the live program had structured IR nodes there, and
nothing was reporting it. Those 84 are now retyped; 7 remain, itemized below.

WHY IT MATTERS FOR THE COUNT. A `\trusted` stub whose blocker is "this field int-erases" is
filed against the emitter's type inference, when the real cause may be that the MIRROR simply
never picked up a retype the live source already has. Field parity is therefore a
conversion-unblocking measurement, not only a hygiene one.

BASELINE: **7 drifted**, all deliberate int-erasures of class-level constant tables (accepted BY
NAME in `INT_ERASED`, so that list can only shrink). The 84 `'ExprIR'` -> `CSLNode` fields the
gate first reported have since been RETYPED in the mirror to match the live source — proof-neutral
(`frontend/Module2_Parser` proves 711 Valid before and after) and corpus byte-inert, but 84 fields
that were opaque integers in the verified artifact now carry the real `emit_ir` child. The
`KNOWN_DRIFT` shape set is retained so the gate keeps recognizing that family if it reappears.
The gate FAILS on anything else, so a NEW divergence is caught while the residue stays visible.

Usage:  bin/check-mirror-field-parity.py [--list]
Exit 1 on a new (non-baseline) drift.
"""
from __future__ import annotations

import ast
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR_ROOT = os.path.join(ROOT, "src/self-annotate/src")
LIVE_ROOT = os.path.join(ROOT, "src/pycsl")

# The measured baseline, as (live annotation, mirror annotation) PAIRS rather than a list of
# 91 field names: the point is the SHAPE of the accepted divergence, so a new field that
# drifts the same documented way is not noise, while a new KIND of drift fails the gate.
KNOWN_DRIFT = {
    # The Module5 construction build retyped the CSL-AST expression children in the LIVE
    # source; the mirror still carries the pre-retype `CSLNode`. Weaker (int-erasing), not
    # unsound. 84 fields, almost all in `frontend/Module2_Parser.py`.
    ("'ExprIR'", "CSLNode"),
    # `Optional['ExprIR']` children, same campaign.
    ("Optional['ExprIR']", "Optional[CSLNode]"),
    ("List['ExprIR']", "List[CSLNode]"),
}

# DELIBERATE int-erasure of class-level CONSTANT tables. The stub generator writes `int` for
# a container type the model does not carry, so these are intentional — but each one is a
# real modelling gap, so they are listed BY NAME rather than by shape: the list can only
# SHRINK, and a NEW int-erased field fails the gate. Three of the four dispatch tables are
# now READ by the L2 dispatch expansion (Module 5 collects them into
# `class_type_str_constants`), which is why their `int` annotation costs nothing today.
INT_ERASED = {
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter", "_CSL_HANDLERS"),
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter", "_PY_EXPR_HANDLERS"),
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter", "_PY_STMT_HANDLERS"),
    ("frontend/Module5_IREmitter.py", "PyCSLToJSONEmitter", "_PY_OP_MAP"),
    ("module6_whyml/ir_scanner.py", "IRScanner", "_MUTATING_METHODS"),
    ("module6_whyml/preamble.py", "PreambleEmissionMixin", "_AXIOM_REGISTRY"),
    # `StructFormat.slots` is the one with a MEASURED conversion consequence: with the
    # mirror field `int`, `StructFormat.arity`'s `len(self.slots)` lowers to an
    # uninterpreted `iter_length self.slots` — barely more than the `val` it would replace,
    # which is why that stub was measured convertible and deliberately NOT converted
    # (VALUE not count). Retype the field and the conversion becomes worth taking.
    ("module6_whyml/struct_format.py", "StructFormat", "slots"),
}


def class_fields(path):
    try:
        src = open(path).read()
    except OSError:
        return {}
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return {}
    out = {}
    for cls in ast.walk(tree):
        if not isinstance(cls, ast.ClassDef):
            continue
        for st in cls.body:
            if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                out[(cls.name, st.target.id)] = ast.unparse(st.annotation)
    return out


def main() -> int:
    show = "--list" in sys.argv
    compared = 0
    known = []
    new = []
    for mp in sorted(glob.glob(os.path.join(MIRROR_ROOT, "**/*.py"), recursive=True)):
        rel = os.path.relpath(mp, MIRROR_ROOT)
        lp = os.path.join(LIVE_ROOT, rel)
        if not os.path.exists(lp):
            continue
        mf, lf = class_fields(mp), class_fields(lp)
        for key, mv in mf.items():
            if key not in lf:
                continue
            compared += 1
            lv = lf[key]
            if lv == mv:
                continue
            rec = (rel, key[0], key[1], lv, mv)
            if (lv, mv) in KNOWN_DRIFT or (rel, key[0], key[1]) in INT_ERASED:
                known.append(rec)
            else:
                new.append(rec)
    print(f"[*] mirror-field-parity: {compared} class-level annotated field(s) compared; "
          f"{len(known)} known drift, {len(new)} NEW drift.")
    if show:
        for d in known:
            print(f"    known  {d[0]}::{d[1]}.{d[2]}  live={d[3]}  mirror={d[4]}")
    for d in new:
        print(f"    [!] NEW  {d[0]}::{d[1]}.{d[2]}  live={d[3]}  mirror={d[4]}")
    if new:
        print("[!] mirror-field-parity: FAIL — a field annotation diverged in a NEW way.")
        return 1
    print("[+] mirror-field-parity: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
