# FINDING — THE L1 FIDELITY PLANE IS RED AT HEAD, AND HAS BEEN FOR A LONG TIME
# (found 2026-09-09 by relaunch #51, at HEAD `37403f79`)

## WHAT IS WRONG

`bin/check-self-annotate-sync.sh` (which is `bin/check-self-annotate-mirror-sync.py`)
**exits 1 at HEAD**, in the main tree and in a pristine worktree with `dirty=0`. It
reports TWO divergences:

    DIVERGED: module6_whyml/expressions.py::ExpressionEmissionMixin._handle_var_expr
              — un-trusted mirror body != live emitter body   (4 lines missing)
    DIVERGED: module6_whyml/stmt_control_flow.py::ControlFlowStmtMixin._handle_for_stmt
              — un-trusted mirror body != live emitter body   (26 lines missing)

Both methods are **CONVERTED, i.e. NOT `\trusted`**. Each carries a real contract in the
mirror (`#@ requires True` / `#@ ensures True` / a long `#@ assigns` list). So these are
methods the campaign counts as *body-verified*, and their bodies are **strict subsets** of
the live emitter's.

## INDEPENDENTLY VERIFIED BY RAW GREP, NOT ONLY BY THE PLANE

    symbol                        live src/pycsl   mirror src/self-annotate
    _iropt_ir_local_vars                4                   0
    _optional_union_locals             12                   0
    _string_char_iter                   2                   0   (stmt_control_flow)

The missing branches in `_handle_var_expr` are the `_iropt_ir_local_vars` read
(`(iropt_val !x)`) and the whole `_optional_union_locals` projection arm. In
`_handle_for_stmt` the missing region includes `str_ci` (the string-character iterator),
`enum_seq`, `extra_locals`, and the `_saved_symtype` machinery.

## HOW LONG

`git log -S` over the MIRROR file returns **zero commits** for `_iropt_ir_local_vars` and
zero for `_optional_union_locals`: they have never been in the mirror in any commit. The
live emitter gained them long ago (`ce71e3ab`, `41a12274`, `b6c417f6`, `2336cc72`,
`50caedae`, `856f0cdb`). Re-running the plane at each of the last 14 commits gives
`rc=1 diverged=2` at every one, so this is NOT this window's doing and not the previous
window's either.

## WHY IT MATTERS — THIS IS A LOWER BOUND, NOT A LINT

L1 (mirror-sync fidelity) is one of the THREE DISJOINT ORACLE PLANES the whole
self-tcb-reduction campaign rests on. Its job is to make "the mirror method we proved is
the emitter method that runs" checkable rather than assertable. While it is red for a
method, the whole-file proof of that mirror file certifies **a body the emitter does not
have** — the same shape as route #51's emission-level finding ("every proof of the
emitter's own if-statement handler ran over a STRICT SUBSET of its reachable states"),
but here at the SOURCE level, which is strictly worse because no emission diff can see it.

**`w49d_expressions`, in flight at the moment of this finding, is proving exactly this
file.** Its verdict, whatever it is, does not cover the two missing branches.

## WHY NOBODY SAW IT — THE CAMPAIGN'S OWN LESSON, FOR THE FOURTH TIME

The plane is DRIVER-RUN, not wired into `bin/run-reference-tests.sh`, which gates on
`doc-coherency` and IR conformance only. A signal nobody collects is not a signal. The
previous windows' "both fidelity planes byte-identical" refers to BYTE-DIFFING TWO
EMISSIONS across a change — a different measurement that cannot see a mirror body that
was never faithful to begin with.

## WHAT IS NOT YET KNOWN (do not assume either way)

  * Whether the two missing branches are REACHABLE in a way that changes emission. The
    plane proves the bodies differ; it does not prove the difference is exploitable.
  * Whether re-syncing the bodies keeps the mirror PROVABLE. `_handle_for_stmt` is 26
    lines short, and the missing region carries the `_saved_symtype` machinery; making it
    faithful may well cost a re-proof of `stmt_control_flow.py` and may not prove at all.
    **If it does not prove, that is the honest cost of making a converted method faithful
    and it must be worked, not hidden** — the alternative is to re-`\trusted` the method,
    which RAISES the trust surface and must be recorded as such.
