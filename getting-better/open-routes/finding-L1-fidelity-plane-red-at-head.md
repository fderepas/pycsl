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

## AND IT IS NOT TWO BODIES — IT IS A WHOLE UNMIRRORED MACHINERY CLUSTER

Every helper the missing branches call is absent from the mirror ENTIRELY (counts are
`grep -rc` over `module6_whyml/`, live vs mirror):

    _union_local_read_projection   live 4   mirror 0
    _string_char_iter              live 2   mirror 0
    _enumerate_seq_recv            live 4   mirror 0
    _classbody_psl_recv            live 3   mirror 0
    _keyword_iter_recv             live 4   mirror 0
    _tparam_iter_recv              live 5   mirror 0
    _split_call_recv_sep           live 9   mirror 0
    _hval_items_recv               live 6   mirror 0
    _zip_irlist_recv               live 6   mirror 0
    iropt_val                      live 6   mirror 0

**THE DISTINCTION THAT MATTERS, AND IT IS THE WHOLE POINT.** A method that is simply
UNMIRRORED is honestly outside the verified set, and the campaign already counts those:
`check-mirror-coverage.py` is GREEN at 550 unmirrored defs / 41 unmirrored files, which is
its accepted ratchet. That is fine — it is a measured, declared gap.

What is NOT fine is a method sitting in the CONVERTED (verified) column whose real body
branches into that unmirrored machinery, with the branches simply deleted from the copy we
prove. `_handle_var_expr` and `_handle_for_stmt` are counted as body-verified and are not.
`check-mirror-coverage` cannot see this, because the helpers it counts as unmirrored are
exactly the ones whose call sites were removed — the two planes' blind spots line up.

## THE FOUR OPTIONS, WITH THEIR HONEST COSTS

  (a) **Mirror the whole helper cluster and re-sync both bodies.** The most faithful and by
      far the most work: ten helper families, and a re-proof of the two SLOWEST mirrors in
      the tree (`expressions.py` and `stmt_control_flow.py`, each >2h).
  (b) **Re-`\trusted` the two methods.** Honest, cheap, and it RAISES the trust surface by
      two markers (456 -> 458). The campaign's own rule says an honest increase beats a
      false verification, so this is a legitimate outcome, not a defeat.
  (c) **Sync the bodies faithfully and let the unmirrored helpers become `\trusted` stubs**
      — the mirror's normal technique for a call it does not verify (the existing
      `self__<m>` avatar machinery, which `check-avatar-frame-parity` and
      `check-shadowed-selfcalls` already police). Cost: roughly ten new `\trusted` stubs, so
      the metric rises to about 466, and the two methods STAY converted with bodies that are
      genuinely the emitter's. **This is the campaign's normal move and the recommended one.**
  (d) Declare the divergence an accepted exception. **REJECTED** — that is exactly what has
      been happening implicitly, and it is what left an L-plane red without anyone knowing.

Whichever is taken, it must be taken with the batteries stopped: `w49d_expressions` and
`w49d_statements` are proving these very files, and editing a file mid-proof produces a
verdict that certifies a superseded artefact (the `w49d_scf` lesson, window #50).
