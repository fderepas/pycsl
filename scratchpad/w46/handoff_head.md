# ===================== START HERE — #46 -> next window =====================
#
# **THREE MORE UNSOUNDNESS ROUTES (#39, #40, #41), ALL CLOSED, ALL NEGATIVE-TESTED
# END-TO-END, AND ALL THREE ARE THE SAME MISTAKE IN THREE DIFFERENT PLACES.** The
# metric is UNCHANGED at markers 456 / grep 481 / offset 25 — not one of these
# needed a new trust stub. Fourteen witnesses added (1033-1046).
#
#   #39  ROUTE #38's OWN REFUSAL WAS WALKED PAST BY TWO LINES OF ORDINARY PYTHON.
#        `c: CM = CM()` is an `AnnAssign`, and #38's binding census read plain
#        `Assign` nodes only; `class CM(Base)` with the protocol on the BASE was
#        never in #38's class set because the scan read each ClassDef's own body.
#        Both re-ran #38's exploit VERBATIM and proved `\result == 0` where Python
#        returns 5.                                   witnesses 1033 / 1035, 1034 ctl
#   #40  THE `...` LITERAL WAS THE INTEGER ZERO. Flagged by relaunch #12 as "a
#        silent WRONG-VALUE erasure ... left alone deliberately" and NEVER PROBED.
#        SIX shapes proved a false contract: `if x:`, `if ...:`, `x == 0`,
#        `<int> is ...`, `x + 5`, `return ...`.          witnesses 1036-1040
#   #41  ROUTES #25/#26/#27 REFUSED THE GUARD AND NOTHING ELSE. The same erased
#        local (a generator expression / non-empty set / non-empty tuple) was
#        exploitable through `== 0`, `< 1` and `+ 5`; and the EMPTY tuple was
#        outside the record entirely, so `() == 0` proved.  witnesses 1041-1046
#
# ## THE ONE LESSON, and it is worth more than the three routes
#
# **A REFUSAL IS ONLY AS SOUND AS THE RESOLUTION IT KEYS ON, AND AN ERASURE IS ONLY
# AS SAFE AS ITS LEAST-CHECKED CONSUMER.**
#
#   * #38 was written as "refuse when I can SHOW this is a context manager". The
#     correct shape is "refuse unless I can SHOW this is modelled". The enumeration
#     of ways to NAME a value is open-ended; the enumeration of MODELLED forms is
#     not. #39's fix is a whitelist and the mirror's 52 `with` sites pass it.
#   * #25/#26/#27 patched the CONSUMER that had been demonstrated (the guard).
#     Route #41 shows the erasure is decidable under EVERY int operator, so the
#     value itself has to stop being a literal. Witness 1044 (`x < 1`) exists
#     precisely to show that an equality-only patch would have been the same
#     mistake one step later.
#   * The fix that worked TWICE is the same one: **make the value OPAQUE, not the
#     consumer refused.** `val function pycsl_ellipsis : int` and per-name
#     `val function pycsl_erased_<x> : int`, both with NO defining axiom, close ten
#     shapes between them and refuse nothing that merely holds or passes the value.
#     PER-NAME MATTERS: one shared constant would let the model prove `x == y` for
#     two distinct erased locals — one unsoundness traded for another.
#
# ## THE TWENTY-THIRD PLANE MAKES THAT SHAPE MECHANICAL
#
# `bin/check-constant-fallthrough.py` (subsecond, static): every Module-6 lowering
# whose FALL-THROUGH is a Why3 CONSTANT. Routes #29, #30, #31, #40 and #41 are ONE
# shape and all five were found by hand, one at a time. MEASURED 8 DECIDING (each
# classified in the gate's baseline) / 10 INERT (`return ""` — not a Why3 term, so
# a syntax error at the use site rather than a decision). It fails on a STALE
# baseline entry too, which is the half that keeps a ratchet honest. Negative-tested
# three ways. **Stated limit: a constant returned from a GUARDED branch mid-handler
# is NOT a fall-through and is not counted** — routes #22/#24 lived there, and the
# instruments for those are `check-getattr-erasure` and `check-computed-rhs-erasure`,
# which watch the real emission.
#
# ## WHAT TO DO FIRST
#
# 1. **CONVERT THE "FAIL-CLOSED BY ACCIDENT" POPULATION INTO DESIGNED REFUSALS.**
#    This window ran ~100 probes; roughly a third of the ones that closed did so on
#    a Why3 TYPE ERROR or an `unbound ... symbol`, not on a refusal and not on an
#    unprovable goal. That is precisely the state route #29 was built to remove for
#    the array spec atoms ("fail-closed BY DESIGN rather than by an unrelated bug a
#    completeness fix could remove at any time"), and it is now the single largest
#    standing hazard. NAMED INSTANCES, all measured this window: a tuple/genexp
#    stored to a FIELD; `set()` and a dict literal in a guard; `frozenset`/`zip`/
#    `enumerate`/`iter`/`reversed`/`memoryview`/`sorted`/`map`/`filter`/`list`/
#    `tuple` bound to a local; a lambda local; a class-variable read (`c.k`); a
#    function-reference call (`k = h; k()`); `return (1,2)`; `if (1,2) == 0`;
#    a tuple-unpack target; `return` inside `finally`; a lemma resting on a
#    `\trusted` fact. Each is one `PIPELINE ERROR` away from being honest.
# 2. **THE MISSING-`use` FAMILY IS 17 FILES AND NONE OF THEM IS A MISSING `use`.**
#    Measured, not estimated: `why3 prove --type-only` over ALL 858 emitted
#    pycsl-reference modules gives SEVENTEEN failures and ZERO
#    `unbound type symbol 'map'/'array'/'matrix'`. My first text census claimed
#    21/16/15/13 files — all false positives from matching inside comments and
#    strings. USE THE TYPE CHECKER, NOT A REGEX. The seventeen are named in the
#    progress log; three of them (0560/0563/0575) are DELIBERATE negative tests.
#    The real remaining names are `iter_length` (0793/0794), `subscript_get` (0807),
#    `int_mem` (0639), `z_` (0303) and `a_len` (the branch-bound list sidecar).
# 3. **THE LAST SLIVER OF #36** is still parked and unchanged — read #45's note
#    before re-spiking; three approaches are already measured and refuted.
#
# ## SETTLED THIS WINDOW, DO NOT RE-DERIVE
#
# * **`@property` IS MODELLED FAITHFULLY.** `c.v` on a `@property` lowers to the
#   real call `(c__v c)`; a contract false of the getter correctly fails. It is a
#   capability, not a gap.
# * **ROUTES #32/#33 HOLD, and I checked the thing that would have unmade them.**
#   Witnesses 1013/1014 and three fresh pre-declared variants ALL fail on an
#   UNDECLARED SIDECAR (`unbound ... 'a_len'`) — the exact "looks like the tool is
#   sound here" shape. So I exercised the same fold logic with a sidecar that DOES
#   exist (a list built by `append` in both arms): the FALSE `len(a) == 2` fails,
#   the TRUE `len(a) == 3` PROVES, the FALSE `a[0] == 1` fails. The poisoning of
#   `_known_collection_sizes` is doing the work; `a_len` is a completeness gap.
# * **A `#@ lemma` CANNOT INJECT AN AXIOM.** `#@ ensures 0 == 1` on a lemma is not
#   proved — Why3 checks the lemma body. `#@ assert 0 == 1` fails too.
# * **THE FOUR STATEMENT KINDS WITH NO MODULE 5 HANDLER ALL REFUSE.**
#   `AsyncFunctionDef`, `AsyncFor`, `AsyncWith`, `TryStar` and `await` are all
#   `PIPELINE ERROR` at the front end, so `check-statement-block-coverage`'s
#   "4 kind(s) with NO Module 5 handler" line is a completeness note, not a hole.
# * **~100 further probes are listed in the progress log** across erased-value
#   equality/ordering/arithmetic, erasure-record bypass positions, dunder
#   protocols, Python-vs-Hoare semantics and the spec surface. All fail-closed.
#
# ## THE `None` RESIDUE — the one thing this window found and did NOT close
#
# `None` lowers to the literal `0` on exactly the same terms as `...` did, and has
# the same three exploits, ALL MEASURED at the window's parent commit:
#
#     x = None; if x == 0: return 7    ->  `\result == 7` PROVED.  Python: 0
#     x = 0;    if x is None: return 7 ->  PROVED.                 Python: 0
#     x = None; return x + 5           ->  `\result == 5` PROVED.  Python: TypeError
#
# **IT IS NOT CLOSED BECAUSE `None`-as-`0` IS LOAD-BEARING IN A WAY `...` IS NOT**:
# `NoneExpr -> "0"` is the Optional convention the union/carrier recognizers and
# every `is None` guard in the mirror are built on, so the opacity fix that worked
# for `...` would break the emitter wholesale. Under that convention the model is
# internally consistent; the defect is that a GENUINE int 0 is indistinguishable
# from `None`. REOPENING CAPABILITY: a tagged value model (the `pyconst_val`/hval
# ADT applied to plain int-typed locals) that can tell "denotes a Python int" from
# "denotes an opaque singleton". CLASSIFY IT AS [CORRECTNESS] TODAY — the value
# model genuinely cannot express the distinction — with the tagged-value-model
# build as the named capability that reopens it.
#
# **THE GENERAL SHAPE, which is the transferable part: A PYTHON SINGLETON MODELLED
# AS AN INTEGER LITERAL IS INDISTINGUISHABLE FROM THAT INTEGER INSIDE THE MODEL, SO
# EVERY COMPARISON AGAINST THAT INTEGER IS DECIDED THE WRONG WAY.**
#
# ## THINGS THAT COST ME TIME
#
# 1. **A HEREDOC TURNED `\result` IN A COMMENT INTO A CARRIAGE RETURN** and broke
#    `expressions.py`. Every probe then reported "closed" — because the pipeline
#    died with `UNEXPECTED PIPELINE ERROR: invalid syntax`. FAIL-CLOSED BY ACCIDENT
#    LOOKS EXACTLY LIKE FAIL-CLOSED BY DESIGN UNLESS YOU READ WHY. The probe loop
#    now prints the extracted reason next to every verdict, and no "closed" is
#    trusted until the reason has been read AND the opaque symbol has been seen in
#    the emission. Write patches with `r"""` or `\\`.
# 2. **A NESTED `def` INSIDE A REFUSAL BROKE `check-mirror-coverage` 550 -> 551.**
#    A new LIVE function has no mirror counterpart and the plane counts it. Found
#    only by running the FULL battery instead of the planes the change "should"
#    touch. Rewritten as an inline loop at each of its four uses.
# 3. **A REGEX CENSUS OF THE MISSING-`use` FAMILY WAS ENTIRELY FALSE POSITIVES.**
#    See item 2 above. The type checker is the instrument.
#
# ## STATE AT HANDOFF
#
#   metric            markers 456 / grep 481 / offset 25 — UNCHANGED across all
#                     three routes and the new plane. A refusal and an opaque value
#                     both cost the trust surface nothing.
#   corpora           pycsl-reference: byte-diff against the worktree-at-HEAD set is
#                     the FOURTEEN NEW WITNESSES AND NOTHING ELSE. Zero pre-existing
#                     emission moved, across all three routes.
#   mirror            emission moves in exactly THREE files by exactly FOUR lines:
#                     `val function pycsl_ellipsis : int` declared in
#                     Module5_IREmitter.mlw and pure_ast.mlw, `visit_Constant`'s
#                     guard going `!value = 0` -> `!value = pycsl_ellipsis` (MORE
#                     faithful than what it replaced), and
#                     `val function pycsl_erased_map_prefixes : int` declared in
#                     statements.mlw (no body moved). All three whole-file re-proofs
#                     were launched detached; see `getting-better/proofs46/`.
#   mirror L3-tc      53/53 (106 hits over 53 files), re-measured after every route
#   fidelity          check-self-annotate-sync + self-annotate-mirror-check output
#                     BYTE-IDENTICAL to HEAD at every step (the pre-existing
#                     `_handle_var_expr` / `_handle_for_stmt` pair, unchanged)
#   planes            all rc=0, plus the new twenty-third. mirror-coverage 550/41 ·
#                     trusted-raises-honesty 68 · dropped-mutation 0/51/11/0 ·
#                     emitted-vacuity 8 known · computed-rhs-erasure 1/0 ·
#                     bespoke-model-drift 27 · ir-field-coverage 4 ·
#                     statement-block-coverage 3 · getattr-erasure 0/7/19 ·
#                     yield-erasure 0/2/1 · shadowed-selfcalls 14 ·
#                     clause-survival 2/853 · avatar-frame-parity 0/7 ·
#                     mirror-loop-annotations 330/5 · mirror-signature-drift 0 ·
#                     untrusted-emitted 861/845/0 · refusal-reachability 0 ·
#                     internal-crash-free 0 · constant-fallthrough 8/10 ·
#                     doc-coherency OK
#   witnesses         1033-1046, fourteen, every one PROVING a contract FALSE of its
#                     own program at its parent commit and failing closed at HEAD
#   docs              `docs/pycsl-translational-reference.md` §T.5.10b REWRITTEN (the
#                     `with` refusal restated as the whitelist it now is, with both
#                     bypasses named), plus new §T.5.12d (the `...` literal) and
#                     §T.5.12e (an erased local is opaque on every read).
#
# ==========================================================================

