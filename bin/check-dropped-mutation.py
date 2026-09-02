#!/usr/bin/env python3
"""check-dropped-mutation.py — the MUTATION-DROP plane.

WHAT IT MEASURES, and why it exists.

Module 5's assignment-family handlers are `if`-chains over the TARGET's AST shape, and
every one of them ends without an `else`. A shape no branch matches produces **no IR at
all**: the statement is not lowered, not refused, not warned about — it simply is not in
the model. That is a fail-OPEN, and it is invisible to every other plane in this campaign,
because the other planes all inspect what WAS emitted. A statement that was never emitted
leaves nothing to inspect.

Relaunch #33 found four instances of the class by hand, and one of them was not
theoretical: `a = b = 5` dropped `b`, and a three-line program with the postcondition
`n <= 0 ==> \\result == 0` — FALSE of the program, which returns 5 — reported
`Verification SUCCESS`. Three of the four are now closed (chained comparison, multi-target
assignment, annotated non-Name store) and one is REFUSED (`for/while ... else`). This gate
exists so the fifth is found by a machine instead of by hand.

CLASSIFICATION. Every assignment-family statement in the scanned populations is put in
exactly one bucket:

  HANDLED     a Module 5 branch matches the target shape and emits IR.
  NORMALIZED  `frontend/desugar.py` rewrites it into a HANDLED shape before Module 5.
  REFUSED     the pipeline raises with a diagnostic (fail-CLOSED — the honest answer for a
              shape that has no sound lowering).
  DROPPED     no branch matches and nothing refuses it. **This is the ratchet.**
  CTXBIND     a `with ... as X` binding. `_py_stmt_with` reads `stmt.body` and the mutex
              annotations and NEVER reads `stmt.items`, so the context manager and the `as`
              name are both absent from the model and the body is spliced in their place.
              It has its OWN ratchet because it is a different kind of gap: modelling it
              needs an `__enter__`/`__exit__` protocol, and today every occurrence in the
              self-annotation mirror is inside a `\trusted` function (measured, all ten),
              while the reference corpus has none. So it is a KNOWN, BOUNDED gap rather
              than a live defect — and this counter is what keeps it bounded.

The ratchet is the DROPPED count. It is NOT allowed to rise. Lowering it means either
adding a sound lowering, adding a normalization, or adding a refusal — in every case the
fail-open becomes something a reader can see.

SCOPE. The four populations that are actually verified or mirrored: the reference corpus,
the self-annotation mirror, `src/pycsl_lib`, and the LIVE emitter — the last one because
`--import-path src/pycsl` makes the pipeline PARSE the live modules as import stubs and
lower their helpers, a fact relaunch #33 learned the hard way when a census over the mirror
alone said "0 victims" and the live tree had two.
"""
from __future__ import annotations

import argparse
import ast
import os
import sys
import warnings

# Parsing 28k statements' worth of source means parsing docstrings full of `\length`,
# `\result` and friends; CPython emits a SyntaxWarning per invalid escape and they are
# NOISE here, not findings.
warnings.filterwarnings("ignore", category=SyntaxWarning)

ROOTS = [
    "test-suite/corpus/pycsl-reference",
    "src/self-annotate/src",
    "src/pycsl_lib",
    "src/pycsl",
]

# --------------------------------------------------------------------------------------
# THE RATCHET — the honest measurement at the tree that introduced this gate (relaunch #33,
# after the chained-comparison / multi-target / annotated-store normalizations landed).
#
#   DROPPED = 1
#     src/pycsl/frontend/pure_ast.py::_merge_str_constants   `out[-1].value += v.value`
#
#   An augmented store through a NON-NAME base. Its plain-assignment twin `a[i].f = v` is
#   already REFUSED by `_py_stmt_assign`, with the reason recorded there: a
#   `List[<record>]` element is emitted PURE/immutable (Why3 forbids a mutable element
#   inside `array`), so there is no sound `<-` store to write back through. The augmented
#   form inherits that boundary and must inherit the refusal too — but refusing it TODAY
#   would reject `pure_ast.py` itself for every mirror that imports it, and the only way to
#   satisfy the refusal is to rebuild the element (`out[-1] = Constant(...)`) inside the
#   PARSER every file goes through. REOPENING CAPABILITY: a sound write-back for a mutable
#   object reached through a subscript — the same one `_py_stmt_assign`'s refusal names.
#   Until then this is a RECORDED fail-open, not an unnoticed one.
# --------------------------------------------------------------------------------------
MAX_DROPPED = 1

# CTXBIND ratchet — `with <expr> as X`. Measured at the tree that introduced this gate:
# 10 in `src/self-annotate/src` (every one inside a `\trusted` function — `_sha256_file`,
# `_run_proofs`, `main`, `_is_false_goal`), 38 in the live emitter, 0 in the reference
# corpus, 0 in `src/pycsl_lib`. REOPENING CAPABILITY: an `__enter__`/`__exit__` protocol
# in the IR, at which point the `as` binding becomes an ordinary store.
MAX_CTXBIND = 48


def _classify_augassign(node: ast.AugAssign):
    t = node.target
    if isinstance(t, ast.Name):
        return "HANDLED", "AugAssign -> Name"
    if isinstance(t, ast.Attribute):
        if isinstance(t.value, ast.Name) and t.value.id == "self":
            return "HANDLED", "FieldAugAssign -> self.<f>"
        if isinstance(t.value, ast.Name):
            return "DROPPED", "augmented store to `<name>.%s` — no branch matches" % t.attr
        return "DROPPED", "augmented store through a non-Name base `.%s`" % t.attr
    if isinstance(t, ast.Subscript):
        if isinstance(t.slice, ast.Slice):
            return "DROPPED", "augmented store to a SLICE `a[lo:hi] op= v`"
        return "HANDLED", "ArraySet (read-modify-write)"
    return "DROPPED", "augmented store to a %s target" % type(t).__name__


def _classify_assign(node: ast.Assign):
    if len(node.targets) > 1:
        return "NORMALIZED", "multi-target `a = b = v` -> one Assign per target"
    t = node.targets[0]
    if isinstance(t, (ast.Name, ast.Tuple, ast.Subscript)):
        return "HANDLED", "Assign -> %s" % type(t).__name__
    if isinstance(t, ast.Attribute):
        if isinstance(t.value, ast.Name):
            # `self.f = v` and `p.f = v` (p in the function symtab) are FieldAssign; a
            # module-global singleton base is a DOCUMENTED no-op boundary, not a silent one.
            return "HANDLED", "FieldAssign -> <name>.%s" % t.attr
        return "REFUSED", "field store through a non-Name base (PYCSL-WHYML-PARAM-COLLECTION-MUT)"
    if isinstance(t, ast.Starred):
        return "DROPPED", "starred assignment target"
    return "DROPPED", "Assign to a %s target" % type(t).__name__


def _classify_annassign(node: ast.AnnAssign, in_init: bool):
    if node.value is None:
        return "HANDLED", "declaration only (no store)"
    if isinstance(node.target, ast.Name):
        return "HANDLED", "AnnAssign -> Name"
    if in_init:
        return "HANDLED", "`__init__` annotated field init (record field TYPE source)"
    return "NORMALIZED", "annotated non-Name store -> plain Assign"


def _init_annassigns(tree: ast.AST):
    protected = set()
    for node in ast.walk(tree):
        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == "__init__"):
            for sub in ast.walk(node):
                if isinstance(sub, ast.AnnAssign):
                    protected.add(id(sub))
    return protected


def scan_file(path: str):
    try:
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
    except (SyntaxError, UnicodeDecodeError, OSError):
        return []
    protected = _init_annassigns(tree)
    rows = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AugAssign):
            bucket, why = _classify_augassign(node)
        elif isinstance(node, ast.Assign):
            bucket, why = _classify_assign(node)
        elif isinstance(node, ast.AnnAssign):
            bucket, why = _classify_annassign(node, id(node) in protected)
        elif isinstance(node, (ast.For, ast.While)) and node.orelse:
            bucket, why = "REFUSED", "loop `else` (desugar.reject_unmodelled)"
        elif isinstance(node, ast.Slice) and node.step is not None:
            bucket, why = "REFUSED", "extended slice `x[lo:hi:step]` (desugar.reject_unmodelled)"
        elif isinstance(node, ast.With) and any(
                it.optional_vars is not None for it in node.items):
            bucket, why = "CTXBIND", "`with ... as X` — the binding is not read"
        else:
            continue
        rows.append((bucket, path, node.lineno, why))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-dropped", type=int, default=MAX_DROPPED)
    ap.add_argument("--max-ctxbind", type=int, default=MAX_CTXBIND)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    counts = {"HANDLED": 0, "NORMALIZED": 0, "REFUSED": 0, "DROPPED": 0, "CTXBIND": 0}
    dropped = []
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for fn in sorted(filenames):
                if not fn.endswith(".py"):
                    continue
                for bucket, path, line, why in scan_file(os.path.join(dirpath, fn)):
                    counts[bucket] += 1
                    if bucket == "DROPPED":
                        dropped.append((path, line, why))

    print("[*] dropped-mutation: %d statement(s) scanned — "
          "%d HANDLED, %d NORMALIZED, %d REFUSED, %d DROPPED, %d CTXBIND."
          % (sum(counts.values()), counts["HANDLED"], counts["NORMALIZED"],
             counts["REFUSED"], counts["DROPPED"], counts["CTXBIND"]))
    if args.verbose or dropped:
        for path, line, why in sorted(dropped):
            print("    DROPPED  %s:%d  %s" % (path, line, why))

    if counts["CTXBIND"] > args.max_ctxbind:
        print("[!] dropped-mutation: CTXBIND RATCHET BROKEN — %d > %d. A `with ... as X` "
              "binding is absent from the model; the gap is bounded, not licensed."
              % (counts["CTXBIND"], args.max_ctxbind))
        return 1
    if counts["DROPPED"] > args.max_dropped:
        print("[!] dropped-mutation: RATCHET BROKEN — %d > %d. A statement Module 5 "
              "neither lowers nor refuses is a fail-OPEN no other plane can see: the "
              "mutation is simply absent from the model, so a contract can be proved "
              "that is FALSE of the program."
              % (counts["DROPPED"], args.max_dropped))
        return 1
    if counts["DROPPED"] < args.max_dropped:
        print("[+] dropped-mutation: DROPPED %d < ratchet %d — lower the constant."
              % (counts["DROPPED"], args.max_dropped))
    if counts["CTXBIND"] < args.max_ctxbind:
        print("[+] dropped-mutation: CTXBIND %d < ratchet %d — lower the constant."
              % (counts["CTXBIND"], args.max_ctxbind))
    print("[+] dropped-mutation: OK (ratchets %d dropped / %d ctxbind)."
          % (args.max_dropped, args.max_ctxbind))
    return 0


if __name__ == "__main__":
    sys.exit(main())
