# STAGED — the L1 `_handle_var_expr` mirror re-sync (ready, NOT landed)

## WHAT IT IS

`l1-handle-var-expr-resync.patch`, generated against `2b933da9`. It is a MIRROR-ONLY
change: it re-inserts, verbatim, the TWO `if` blocks the mirror's `_handle_var_expr` is
missing relative to the live emitter —

    if name in getattr(self, "_iropt_ir_local_vars", set()):   -> (iropt_val !x)
    if name in getattr(self, "_optional_union_locals", set()): -> the union read projection

The live emitter is NOT touched, so the change is **corpus-inert by construction**: the
compiler behaves identically, only the self-annotation mirror's own text moves.

## WHY IT MATTERS

`check-self-annotate-mirror-sync` is an **L-PLANE**, and it has been RED at HEAD for a
long time. Two un-`\trusted` (i.e. COUNTED AS VERIFIED) mirror methods carry bodies that
are strict SUBSETS of the live emitter, so the proof proves something the emitter does not
do. This patch closes one of the two.

## MEASURED (generation #3, independently re-derived at HEAD — not inherited)

    fidelity BEFORE   2 divergence(s) over 841 verbatim-checked un-trusted functions
    fidelity AFTER    1 divergence(s) over 842        <-- _handle_var_expr now MATCHES
    18-plane collector  17 green, the 1 red being the REMAINING divergence
                        (`_handle_for_stmt`), i.e. NO ratchet moved and nothing else broke

The exact gap, by AST statement count at HEAD: live 23 statements vs mirror 21.

## WHY IT IS NOT LANDED YET, AND WHAT LANDING OWES

`_handle_var_expr` is UN-`\trusted`, so its new body must PROVE: landing owes a whole-file
re-proof of `module6_whyml/expressions.py` (3-4h, one of the two slowest mirrors in the
tree). At the time of staging, `w51g2_expressions` was ALREADY RUNNING on that same file
as route #57's owed mover. Landing the mirror change mid-proof would not corrupt that run
(it had already emitted), but it would make its rc attest to the PRE-patch tree while
appearing to attest to the post-patch one — the attribution loss that cost route #42 a
bisect.

**SEQUENCE: collect `w51g2_expressions` -> record its verdict -> apply this patch ->
re-prove `expressions.py` -> land only if that proof is rc=0.**

## THE OTHER HALF, STILL UNDECIDED

`_handle_for_stmt` carries **37 of 99** live statements while counted as VERIFIED — a far
bigger lie than this one was, and it is NOT addressed here. Port the missing statements or
re-`\trusted` it and let the metric rise 456 -> 457. Do not leave it counted as verified.
Blocked the same way on `w51g_scf`.
