#!/usr/bin/env python3
r"""check-dropped-mutation.py — the MUTATION-DROP plane.

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
  TRYFINAL    a `try ... finally:` / `try ... else:` whose block is NOT emitted. Module 5
              DOES carry `orelse` and `finalbody` into the IR; Module 6's
              `_handle_try_stmt` reads `stmt.body` and `stmt.handlers` and neither of the
              other two. #33 emits the `finally` block in the ONE case that is expressible
              by appending it — no handlers, and no `raise` anywhere in the LOWERED body,
              so no other exit path exists — and counts the rest here. Python runs
              `finally` on EVERY exit path, so the residue is a fail-OPEN with its own
              ratchet. REOPENING CAPABILITY: run the block on the handler arms and on a
              `Return_t` re-raise arm, which needs the function's return-exception name at
              that point in the emitter.
  DANGLING    a CONTRACT-level `#@` block with nothing after it to attach to (it runs to
              end-of-file). Module 3 binds an annotation block to the node that FOLLOWS it;
              a block with no follower is silently discarded and the run still reports
              `[+] Verification SUCCESS! All contracts formally proven.` — a contract the
              author wrote, that was never checked, under a message that says everything
              was. MEASURED: a trailing `#@ ensures \result == 99` after a function
              returning 1 proves SUCCESS. Statement-level directives (`assert`, `assume`,
              `ghost`, `loop ...`, `label`, `reveal`) are EXCLUDED — a trailing `#@ assert`
              is the last statement of a body and attaches correctly; three corpus files
              (0710/0711/0712) end that way and are not findings.
              **RATCHET 0, a HARD 0** across all four populations plus `python-reference`
              and the negative corpus. Fixing it properly belongs in `Module3_Weaver`
              (raise on a `contracts_map` key nothing consumed); until then this counter
              guarantees the tree never grows one.
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

THE SWEEP THAT PRODUCED THIS PLANE, AND ITS NEGATIVE RESULTS — recorded so the next window
does not re-derive them. The question is always the same: which fields of the node does the
lowering never mention?

  MODULE 5, Python-AST handlers (`_PY_EXPR_HANDLERS` / `_PY_STMT_HANDLERS`, 39 of them):
    14 had an unmentioned field, 11 benign (`ctx`, `type_comment`, `kind`, or a two-line
    delegator). THREE were real and all three are closed or ratcheted: the chained
    comparison, the multi-target assign, the annotated non-Name store.
  MODULE 5, list-head reads ("reads only element `[0]` without iterating"): FOUR —
    `_py_expr_compare.ops`/`.comparators` (fixed), `_py_stmt_raise.args` (benign, the
    exception payload), `_py_stmt_assign.targets` (the proved-false-postcondition one).
  MODULE 5, CSL annotation handlers (`_csl_*`, 79 of them, against the node classes in
    `Module2_Parser.py`): **ZERO drop a field.** The `#@` lowering surface is COMPLETE on
    this axis. Independently confirmed end-to-end: a deliberately VIOLATING body was
    REJECTED for `\forall`, `\exists`, `\old`, `\old(a[i])`, `\old(self.f)`, a call-site
    precondition and a `\length` range.
  MODULE 6, `_handle_*` lowerings (against the `StmtIR`/`ExprIR` dataclasses in
    `ir_schema.py`): **only THREE**, and after this window's `finalbody` and `orelse` fixes
    the semantic residue is ZERO — what is left is `ForStmt.line`, `ForStmt.lineno`,
    `ForStmt.allow_iteration_mutation` and `WhileStmt.line`, all metadata.

  DIRECTIVE WIRING (all 61 `#@` names in `test-suite/annotations.md`, checked against
    grammar / weaver / Module 5 / `core_ir_semantic` / Module 6): **no directive is
    parsed-but-inert.** Every name absent from a late stage is a FRONT-END check that
    legitimately never reaches the IR, and the two that look most like holes were traced
    to their consumers: `allow_finalizer` is the UB-7.5 escape and BOTH the check and the
    escape live in `Module3_Weaver.visit_ClassDef`; `allow_iteration_mutation` is the
    UB-7.1 escape, checked in the `pycsl.py` driver via
    `IRScanner.find_iteration_mutations`, which reads the flag off the IR statement. So
    Module 6's `_handle_for_stmt` not reading that field is correct, not a drop.

  MODULE 3 ATTACHMENT (which `#@` block binds to which node) — PARTLY swept, and it has a
    family: **a directive attached to the wrong KIND of target is silently ignored**, and
    the run still reports success. Three shapes measured end-to-end:
      · a contract block with NO follower — the DANGLING category below. FIXED: the weaver
        now refuses it (census was 0).
      · `#@ loop invariant` / `#@ loop variant` NOT immediately before a `for`/`while` —
        accepted and ignored. CENSUS 1: `pycsl-reference/0299.py` carries two vestigial
        loop annotations directly above a bare `return n`. A refusal is therefore NOT
        inert; it needs that test cleaned first (the lines are meaningless, so the edit
        should be emission-inert — verify before landing).
      · a FUNCTION-level contract (`#@ ensures ...`) directly above a `class` — accepted
        and ignored. CENSUS 0 everywhere, so a refusal here IS inert. Not built: it wants
        the same pass as the loop case, and they should land together.
    Also noted while measuring: a `#@` sequence can appear INSIDE a docstring
    (`src/pycsl/agents/agent-infer-invariants.py:6`), where it is not a directive at all.
    Any raw-source scan of `#@` must expect that; the DANGLING check is safe from it only
    because it additionally requires end-of-file.

A PIPELINE ASYMMETRY, found while tracing where the normalization pass had to live, and
recorded because it is the same bug class one level up: **`ir_resolve.resolve`'s dependency
sub-pipeline does NOT run `exec_splice.splice_constant_exec`.** The main pipeline
(`pycsl.py`) splices a constant `exec("...")` into its parsed straight-line body before
Module 5; the dependency path goes `Module1 -> Module2 -> Module3.process() ->
Module5_IREmitter(unified)` with no splice, so a constant `exec` in an IMPORTED module
would have its statements simply absent from that module's IR. CENSUS: **2 sites, both in
main corpus files (0642, 0643), 0 in any dependency** — so it is a latent asymmetry today.
FIX: one call, in the same place `Module5_IREmitter.generate_json` puts the desugar pass
(and check `resolve`'s trust status in the mirror first — see the lesson about new methods).

LIBRARY-OPERATION PROBES, same false-contract method, all CLEAN (conservative, never
unsound): `d.get(k, default)` with and without the key present; `a.append(v)` then
`len(a)`/`a[-1]`; `s.startswith` / `s.replace` / `s.find` (the opaque string model rejects
BOTH the true and the false contract — incomplete, not wrong); `del d[k]` then `k in d`;
`except ... as e`; list `+=`; negative indexing; and Python's FLOOR `//` and `%` with a
NEGATIVE DIVISOR, where `7 // -2 = -4` and `7 % -2 = -1` both prove and the Euclidean
answers `-3` / `1` are REJECTED — a place a Why3 backend could very easily have been wrong
and is not.

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
import re
import sys
import warnings

# Parsing 28k statements' worth of source means parsing docstrings full of `\length`,
# `\result` and friends; CPython emits a SyntaxWarning per invalid escape and they are
# NOISE here, not findings.
warnings.filterwarnings("ignore", category=SyntaxWarning)

_STMT_LEVEL = ("assert", "assume", "ghost", "loop", "label", "reveal", "unfold", "havoc")

ROOTS = [
    "test-suite/corpus/pycsl-reference",
    "test-suite/corpus/python-reference",
    "test-suite/corpus/negative",
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
# corpus, 0 in `src/pycsl_lib`; 48 -> 50 when the scan was widened to the
# `python-reference` and `negative` corpora for the DANGLING check (two more there). REOPENING CAPABILITY: an `__enter__`/`__exit__` protocol
# in the IR, at which point the `as` binding becomes an ordinary store.
MAX_CTXBIND = 50

# TRYFINAL ratchet — a `try/finally` or `try/else` whose block is still dropped. Measured
# after #33 emitted the safe case: the THREE CONVERTED, PROVED mirror methods that had a
# dropped `finally` are FIXED (`pure_ast.visit_Try`, `pure_ast.visit_TryStar`,
# `functions._refine_tuple_return_type` — each one a save/restore whose restore was absent
# from the model), and the residue is the shapes with handlers or with a jump out of the
# try body. 0 in the reference corpus.
MAX_TRYFINAL = 9

# DANGLING ratchet — a HARD 0. See the class list above. Measured across
# pycsl-reference, python-reference, the negative corpus, the mirror, `src/pycsl_lib` and
# the live emitter: not one contract-level `#@` block runs to end-of-file.
MAX_DANGLING = 0


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


def _jumps_out(stmts) -> bool:
    """Does any statement in `stmts` (recursively) leave the block other than by falling
    off the end? Each of these lowers to a `raise` in the emitted WhyML, which is exactly
    what makes appending the `finally` block unfaithful."""
    for st in stmts:
        for sub in ast.walk(st):
            if isinstance(sub, (ast.Return, ast.Break, ast.Continue, ast.Raise)):
                return True
    return False


def _init_annassigns(tree: ast.AST):
    protected = set()
    for node in ast.walk(tree):
        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == "__init__"):
            for sub in ast.walk(node):
                if isinstance(sub, ast.AnnAssign):
                    protected.add(id(sub))
    return protected


def scan_dangling(path: str):
    """CONTRACT-level `#@` blocks that run to end-of-file with nothing to attach to."""
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except (UnicodeDecodeError, OSError):
        return []
    out, i = [], 0
    while i < len(lines):
        if lines[i].strip().startswith("#@"):
            j, kinds = i, []
            while j < len(lines) and (lines[j].strip().startswith("#")
                                      or not lines[j].strip()):
                m = re.match(r"#@\s+\\?([a-z_]+)", lines[j].strip())
                if m:
                    kinds.append(m.group(1))
                j += 1
            if j >= len(lines) and any(k not in _STMT_LEVEL for k in kinds):
                out.append((i + 1, ",".join(kinds)))
            i = j
        else:
            i += 1
    return out


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
        elif isinstance(node, ast.Try) and (node.finalbody or node.orelse):
            if node.finalbody and not node.handlers and not _jumps_out(node.body):
                bucket, why = "HANDLED", "`try/finally`, no handlers, no jump out — emitted"
            elif node.orelse and not node.finalbody and not _jumps_out(node.orelse):
                bucket, why = "HANDLED", "`try/else`, else cannot raise — appended to the try body"
            else:
                bucket, why = "TRYFINAL", (
                    "`try/%s` block not emitted (%s)"
                    % ("finally" if node.finalbody else "else",
                       "has handlers" if node.handlers else "jumps out of the try body"))
        else:
            continue
        rows.append((bucket, path, node.lineno, why))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-dropped", type=int, default=MAX_DROPPED)
    ap.add_argument("--max-ctxbind", type=int, default=MAX_CTXBIND)
    ap.add_argument("--max-tryfinal", type=int, default=MAX_TRYFINAL)
    ap.add_argument("--max-dangling", type=int, default=MAX_DANGLING)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    counts = {"HANDLED": 0, "NORMALIZED": 0, "REFUSED": 0, "DROPPED": 0,
              "CTXBIND": 0, "TRYFINAL": 0, "DANGLING": 0}
    dropped = []
    dangling = []
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for fn in sorted(filenames):
                if not fn.endswith(".py"):
                    continue
                full = os.path.join(dirpath, fn)
                for bucket, path, line, why in scan_file(full):
                    counts[bucket] += 1
                    if bucket == "DROPPED":
                        dropped.append((path, line, why))
                for line, kinds in scan_dangling(full):
                    counts["DANGLING"] += 1
                    dangling.append((full, line, kinds))

    print("[*] dropped-mutation: %d statement(s) scanned — "
          "%d HANDLED, %d NORMALIZED, %d REFUSED, %d DROPPED, %d CTXBIND, %d TRYFINAL, "
          "%d DANGLING."
          % (sum(counts.values()), counts["HANDLED"], counts["NORMALIZED"],
             counts["REFUSED"], counts["DROPPED"], counts["CTXBIND"],
             counts["TRYFINAL"], counts["DANGLING"]))
    if args.verbose or dropped:
        for path, line, why in sorted(dropped):
            print("    DROPPED  %s:%d  %s" % (path, line, why))

    for path, line, kinds in sorted(dangling):
        print("    DANGLING   %s:%d  `#@ %s` block with nothing to attach to" % (path, line, kinds))
    if counts["DANGLING"] > args.max_dangling:
        print("[!] dropped-mutation: DANGLING RATCHET BROKEN — %d > %d. A contract block "
              "with no following node is DISCARDED, and the run still reports "
              "`All contracts formally proven`."
              % (counts["DANGLING"], args.max_dangling))
        return 1
    if counts["TRYFINAL"] > args.max_tryfinal:
        print("[!] dropped-mutation: TRYFINAL RATCHET BROKEN — %d > %d. Python runs a "
              "`finally` block on EVERY exit path; a dropped one is a fail-OPEN."
              % (counts["TRYFINAL"], args.max_tryfinal))
        return 1
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
    if counts["TRYFINAL"] < args.max_tryfinal:
        print("[+] dropped-mutation: TRYFINAL %d < ratchet %d — lower the constant."
              % (counts["TRYFINAL"], args.max_tryfinal))
    print("[+] dropped-mutation: OK — measured %d dropped / %d ctxbind / %d tryfinal / "
          "%d dangling (ratchets %d / %d / %d / %d)."
          % (counts["DROPPED"], counts["CTXBIND"], counts["TRYFINAL"], counts["DANGLING"],
             args.max_dropped, args.max_ctxbind, args.max_tryfinal, args.max_dangling))
    return 0


if __name__ == "__main__":
    sys.exit(main())
