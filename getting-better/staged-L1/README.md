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

---

# THE SECOND HALF — `_handle_for_stmt`, DECIDED (generation #3)

`l1-both-halves-var-expr-and-for-stmt.patch` supersedes the single-half patch above and
takes the fidelity L-plane to **ZERO divergences**.

## THE DECISION, AND WHY IT WENT THAT WAY

The mirror's `_handle_for_stmt` carried **37 of 99** live top-level statements — measured
another way, **99 source lines against 754**, and **789 AST nodes against 4059**. It was
un-`\trusted`, i.e. COUNTED AS VERIFIED.

Porting the missing body is a session-scale build with low landing confidence (it must not
merely be copied but PROVE, frame included). Re-`\trusted`-ing it is honest, cheap, and the
metric rises 456 -> 457 — **the correct direction**: the trust surface was always this big
and only the bookkeeping said otherwise. **DECIDED: re-`\trusted`.**

## THE TRAP THAT DECISION WALKS INTO, AND IT IS NOT OBVIOUS

**Going BACKWARDS from verified to `\trusted` is NOT free, because it converts a PROVEN
frame into an ASSUMED one.** The `assigns` clause on the verified mirror was proven — but
proven *of the 37% body*, which genuinely writes only 3 `self` fields. As a `\trusted`
stub that same clause becomes an ASSUMPTION about the REAL emitter, and the real emitter
writes more.

Measured on the live body: `_handle_for_stmt` writes **10** `self.<field>`s, and **SEVEN
were absent** from the declared frame —

    _for_target_is_pyval   _in_loop_spec        _keyword_locals    _pyast_loop_variant_len
    _pyast_stmt_locals     _pyval_locals        _tparam_locals

Marking it `\trusted` without widening would therefore have introduced a FALSE ASSUMPTION
in the very increment that was supposed to make the file honest. The frame is widened to
25 fields and the result TYPE-CHECKS (`L3-tc ✓`), so all seven are in scope.

**GENERAL RULE, worth carrying: when a partially-modelled VERIFIED method is re-`\trusted`,
its `assigns` must be RE-DERIVED FROM THE LIVE BODY, never inherited from the proof that
covered the subset.**

## MEASURED (combined, both halves)

    fidelity            0 divergence(s)  — the L-plane is GREEN
    18-plane collector  ALL 18 GREEN
    metric              markers 456 -> 457 (grep 482, offset 25, unattached 0)
    mirror emissions    exactly 2 MOVED — expressions.mlw (half one) and
                        stmt_control_flow.mlw (half two); 0 GONE, 0 APPEARED
    corpus              INERT BY CONSTRUCTION — `git diff --name-only` touches ONLY
                        `src/self-annotate/`, so the live emitter is byte-identical

## WHAT LANDING OWES

Two whole-file re-proofs, one per moved mirror: `module6_whyml/expressions.py` and
`module6_whyml/stmt_control_flow.py`. Both were being proved by queue G for OTHER reasons
at staging time, which is why this is staged rather than landed.

**A widened frame on a trusted stub makes its effect BIGGER, so callers assume LESS. That
is the conservative direction, but it can still cost a caller that relied on one of the
seven fields surviving the call — the `stmt_control_flow.py` re-proof is what measures it,
and it must be run before this lands.**
