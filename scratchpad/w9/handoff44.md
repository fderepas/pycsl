# ===================== START HERE — #44 -> next window =====================
#
# **THE INHERITED STATE WAS NOT WHAT THE HANDOFF SAID IT WAS, IN TWO PLACES.** Both were
# found by re-deriving rather than inheriting, and both are now fixed:
#
#   1. `o_scf.rc = 1`. #43's proof queue left 47 rc files; 46 are rc=0 and ONE is rc=1.
#      All 15 unproven goals sit in `controlflowstmtmixin___handle_try_stmt'vc` and every
#      one is a `termination` or `index in array bounds` sub-goal. CAUSE: route #21's
#      mirror sync copied the LIVE body over the mirror body and thereby DELETED NINE
#      `#@ loop invariant` / `#@ loop variant` lines. The live emitter carries no `#@`
#      annotations, so a verbatim body copy strips the mirror's silently. **Only the
#      whole-file proof can see this** — mirror-sync compares bodies MODULO annotations,
#      L3-tc sees types, byte-diff sees live files, vacuity sees emptiness, the marker
#      count sees `\trusted`. Six green planes, one 30-minute red one.
#      Now held by `bin/check-mirror-loop-annotations.py` (sub-second).
#
#   2. `avatar-frame INHERITED` is **7, not 1**, and the plane has been RED since
#      a3e74638. #43's three "agreeing" measurements all pointed `--emit-dir` at
#      directories with NO MIRROR EMISSIONS in them (a CORPUS emit dir contains no
#      `self__` avatar; two others held zero `.mlw`). The gate scanned 0 avatars, found 0
#      frameless ones, and printed a green 0 — which reads exactly like a tightening.
#      Restored to the measured 7 and the whole `--emit-dir` gate family is now guarded.
#
# ## FOUR NEW UNSOUNDNESS ROUTES, #22-#25 (three closed, #25 open)
#
#   #22  `getattr(obj, "field")` on a DECLARED record field was erased to the DEFAULT
#        (or, for the 2-arg form, a fabricated 0). Proved `\result == 0` where Python
#        returns 7. CLOSED AS A CAPABILITY — the comment's own licence ("a field the
#        record DECLARES is present") turned into a machine check against
#        `_emitted_record_field_labels`. Witnesses 0991 (false) / 0992 (true).
#        It had also made ROUTE #21's OWN REFUSAL dead code:
#        `getattr(stmt, "finalbody", None)` on `TryStmt` lowered to `if (0 <> 0)`.
#   #23  An augmented store could VANISH. `_py_stmt_augassign` was `if/elif/elif` with NO
#        `else`. `self.items[0].v += 5` and `e.v += 5` both proved `\result == 0` where
#        Python returns 5. CLOSED: unsupported bases REFUSED, `p.f op= v` made a
#        CAPABILITY. `dropped-mutation` DROPPED **1 -> 0**. Witnesses 0993/0994/0995.
#   #24  A call whose CALLEE is not a plain name (`type(self)(...)`) erased to the LITERAL
#        `0`. CLOSED with an APPLIED `val opaque_dynamic_call`. `computed-rhs-erasure`
#        **2 -> 1**. Witness 0996.
#   #25  **OPEN, DEMONSTRATED, NOT YET FIXED.** A generator expression bound to a local
#        and consumed in a guard: `g = (i for i in [1,2,3]); if g: return 7; return 0`
#        proves `\result == 0` while Python returns 7 (a generator object is ALWAYS
#        truthy; the literal `0` never is). Probe: `scratchpad/w9/probes/g3.py`.
#        The site is `expressions.py`'s `if t in ("UnknownPyExpr", "GenExp"): return "0"`,
#        whose comment argues "GenExp stays exactly as inert as it was" — inert is not
#        sound. PLANNED FIX and why it must be narrow: an AST census finds 711 generator
#        expressions tree-wide but only **ONE** bound to a NAME
#        (`src/pycsl_lib/json/tool.py:98`); all the rest are inline argument positions
#        (`sum(... for ...)`, `any`, `all`). Making the fallback opaque unconditionally
#        moves ~101 mirror+corpus emissions and buys many re-proofs. Make it opaque ONLY
#        for the ASSIGNMENT-RHS position — byte-inert for every inline site, closes the
#        route, and touches exactly one tree site to re-measure.
#        The `Slice` sibling (`s = a[1:3]; if s:`) was probed too and correctly FAILS.
#
# ## THE RULE THAT FOUND #22, #24 AND #25 — use it first
#
# **AN ERASURE TO A LITERAL IS ONE `if` AWAY FROM A FALSE PROOF; AN ERASURE TO AN OPAQUE
# VALUE IS NOT. So probe an erasure by CONSUMING IT IN A GUARD, never by reading it.**
# This is sharper than "probe the erasure" and it was learned the hard way: for #24 the
# field-read probe (`o = type(self)(); return o.v`) FAILED, and I nearly wrote the site off
# as fails-safe. Only the truthiness test exposed it. The defect is never that the value is
# lost — it is that the model gets to DECIDE A BRANCH on a value it invented.
# `grep -n 'return "0"'` in `module6_whyml/expressions.py` lists the remaining candidates.
#
# ## THE OTHER RULE, four instances in one window
#
# **A GATE THAT CANNOT DISTINGUISH "NOTHING IS WRONG" FROM "I LOOKED AT NOTHING" IS NOT A
# GATE.** This window alone: a refusal that never fired (#43's route-19 narrowing), a
# negative test whose `sed` deleted nothing, a DECLARED-pin that was unreachable by
# construction, and four planes that report green on an empty `--emit-dir`. Two of those
# four actively invite the mistake — `computed-rhs-erasure` prints "0 < ratchet — LOWER THE
# CONSTANT" and `emitted-vacuity` prints "known erasure(s) NO LONGER erased — REMOVE FROM
# KNOWN_ERASURES". All four now exit 2 below a minimum emitted-mirror count.
# **Always run the negative test, and check it fails for the RIGHT REASON.**
#
# ## THREE NEW PLANES
#
#     bin/check-mirror-loop-annotations.py          ratchet 330 lines / 5 files
#         Per-file floor on the mirror's IN-BODY `#@` directives (loop invariant/variant,
#         ghost, assert, check, reveal, label). A contract clause sits ABOVE the `def` and
#         survives a body copy; an in-body directive does not. Sound in one direction:
#         such a line is pure proof support, never a liability.
#     bin/check-getattr-erasure.py                  DECLARED 0 (PINNED) / ABSENT 7 / UNKNOWN 19
#         The route-#22 regression gate. Classifies every `_lower_getattr` fall-through by
#         WHY the field did not resolve. Drives the real emission (a static scan cannot
#         tell DECLARED from ABSENT). UNKNOWN 19 = objects of type `Any`/`object`/non-record
#         mixin, where neither presence nor absence is establishable — not demonstrated
#         exploitable, not sound by argument either, so held by a ratchet.
#     the zero-input guard   in avatar-frame-parity, yield-erasure, computed-rhs-erasure
#                            and emitted-vacuity (see above)
#
# ## HOW TO RUN THE PLANES (all of them need the opam PATH)
#
#     export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
#     ./scratchpad/w9/mirror_emit.sh <repo> <outdir>     # 53 mirror .mlw, --import-path
#     ./scratchpad/w9/l3sweep.sh <out.txt>               # L3-tc 53/53 (each file prints 2)
#     bash bin/byte-diff-sweep.sh <outdir>               # pycsl-reference, 820
#     bash scratchpad/w8/pyref_sweep.sh <repo> <outdir>  # python-reference, 2142 + 75 refused
#     bin/check-emitted-vacuity.py --emit                # WITHOUT --emit it now exits 2
#     bin/check-avatar-frame-parity.py --emit-dir <MIRROR emit dir>   # NOT a corpus dir
#
# A worktree at the parent commit is the negative-test rig, and every witness this window
# was flipped against one: `git worktree add -f --detach /tmp/pycsl-baseNN <parent>`, then
# symlink `.venv` into it.
#
# ## SETTLED THIS WINDOW, DO NOT RE-DERIVE
#
# * `suite.rc`/`suite2.rc` = 1 in `scratchpad/w7`: those were `run-reference-tests.sh` runs
#   with 102 of 3123 failing, and the failures are Rocq-required tests (0211-0220) plus a
#   proof tail — i.e. the opam PATH was missing (instrument fact (cd)). Identical logs,
#   4.5h apart. Re-run cleanly this window; see `scratchpad/w9/suite_full.log`.
# * A `%` OPERATOR in a LIVE function's source makes the self-annotation preamble emit
#   `pycsl_div`/`pycsl_mod` into EVERY mirror that imports that module. Use f-strings.
# * `type(t).__name__` in a diagnostic lowers to `int_to_string (get___name__ (py_type t))`
#   and `t` is an `emit_ir` there — an L3-tc rejection. Use a literal.
# * CLOSING AN ERASURE UNCOVERS A TYPE ERROR. Making `getattr(stmt,"finalbody")` faithful
#   immediately produced an L3-tc rejection, because `finalbody` is an `array emit_ir` and
#   the int-truthiness form `x <> 0` is ill-typed on it. The repair and the erasure fix
#   must land in the same increment.
# * The metric has not moved: **markers 456 / grep 481** across all four routes. Three of
#   the four were closed WITHOUT a re-trust, two of them as capabilities.
#
# ==========================================================================

