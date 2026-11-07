# ROUTE #268 — A CROSS-MIXIN `\trusted` STUB UNDER-DECLARED ITS FRAME; FIVE VERIFIED CALLERS PROVED FALSE FIELD-UNCHANGED CLAIMS

**Status: OPENED + REPAIRED (gen #36, 2026-10-17) at 487c4789 (frame(#49): survival TRAP 1541 -> 1445 ...).**
Found by the slow-plane repair agent while fixing `check-assigns-writes-survival` (declaring three per-loop fields
exposed it). Pre-dates gen #36.

## Defect
In `src/self-annotate/src/module6_whyml/stmt_control_flow.py` the cross-mixin stub for `_stmts_to_whyml` claimed
`#@ assigns self._in_spec` only; the real method writes 14+ fields the class declares. Verified callers
(`_handle_while_stmt`, `_handle_if_stmt`, `_handle_match_stmt`, `_handle_try_stmt`, `_try_union_is_none_match`)
therefore proved `ensures { self._for_idx_init = old self._for_idx_init }`-style frame claims that the real emitter
violates (measured: `while k < 1: for i in range(3, 5): ...` changes `_for_idx_init` '0' -> '3'). Reproducer:
scratchpad slowfix/repro/{run.py,prog.py} (session scratch).

## Repair
The stub lists every declared field of the real method's frame; the five callers and `_handle_for_stmt` widened
to match (true of what they write). Driver-verified: `--slow` 84/84, corpus/pyref 0 MOVED, mirror 3 MOVED
(stmt_control_flow, statements, Transpiler aggregate), `--fun _handle_while_stmt` proves; stmt_control_flow
whole-file rc=0 (executor); statements + Transpiler whole-file OWED.

## Lesson
A `\trusted` stub's declared frame IS the callers' assumption (lesson g5(ii)); an under-declared frame is
SOUNDNESS debt. The survival/underdeclaration planes did not catch this because the fields were not declared.
