# cross-mixin-declaration-stubs-impl.md — implementation plan (driver run #3, 2026-10-30)

Inputs: `cross-mixin-declaration-stubs.md` (dc1, report) and `cross-mixin-declaration-stubs-response.md` (independent fable
review, Gate R satisfied: oracle runs O1-O9 cited, incl. Why3 clone-refinement spikes O6/O7 and the import refutation O4).
Both agree: modelling choice, not a fundamental wall; order R0 -> R1 -> R2a -> R3 -> (R2b) -> R4; R7 (relabel as
`\abstract` / bare `requires_method`) is trust laundering and is FORBIDDEN; no marker drops before a checking plane exists.

## 1. FIRST ACTION — Gate S (make-or-break spike, refutation exit)

Widen the 12 + 1 under-stated declaration frames (and the `_seq_operand` window's `raises`) to the definition's text
(R1) in the executor's tree and run, through heavy.sh, the WHOLE-FILE proofs of the affected mirror files
(`stmt_control_flow.py`, `statements.py`, `expr_ghost_spec_ops.py`, `expr_ghost_collections.py`, `expressions.py` --
HEAVY_LOW=1; emit-diff first per lesson (r): only files whose emission changes need the proof).
- PASS: every changed file proves 0 non-Valid (the four verified control-flow callers' VCs cannot change truth value, O9).
- REFUTE: a changed file no longer proves -> STOP, record which VC depended on the narrow frame (that would be a REAL
  false proof today: escalate it as an open route), no build.
- A solver-budget artefact (Timeout / OOM) is re-run, never a verdict.

## 2. Build (only after Gate S PASS), one commit per increment, brief rule-5 battery on the final HEAD

B0 (R0): `bin/check-trusted-frame-honesty.py` resolves a declaration to its definition through the live MRO (the
   resolution `_self_write_fixpoint` already uses for call edges) and includes the `requires_method` windows; it must
   report the 12 + 1 deltas RED on the base tree (show it) and green after B1. Ratchet, never a loosened gate.
B1 (R1): the frame / raises widening of Gate S, committed.
B2 (R2a): a pure-AST plane `bin/check-declaration-conformance.py` (wired into `bin/run-soundness-planes.sh`, ratchet
   style): for EVERY declaration (`\trusted` stub with no live def in its class, or `requires_method` window) resolve the
   definition and check (a) projected frame inclusion decl ⊇ def (projection onto the declaring file's record fields),
   (b) raises ⊇, (c) requires / ensures TEXT-equal (a non-trivial pre/post is reported as needing R2b and fails the
   plane), (d) signature refinement (report the `ExprIR` vs `Dict` type-layer mapping explicitly). Row 16
   (`_handle_return_stmt`, a base/override pair) goes through the existing #277/#278 override path, not this plane.
   Negative-test the plane: a scratch copy with one frame narrowed back must turn it RED.
B3 (R3): delete the 6 unapplied declarations in `statements.py` ONLY if the plane and the sync / mirror checks accept it;
   report them as "removed by absence", not as capability.
B4 (R4, conditional on B2 green + ratcheted): introduce `#@ declared_in <file>::<Class.m>` in place of `#@ \trusted` for
   declarations the B2 plane checks; `bin/count-trusted-directives.py` reports it as a DISTINCT class next to the
   `\trusted` count; `check-trusted-reasons.tsv` rows move accordingly; the 14 trusted definitions stay counted. Announce
   as "-N markers, -3 TCB" (net). Every doc surface the new directive touches (doc-coherency: annotations.md,
   README, the three reference docs, a skill) is updated. If the directive cannot be made to emit EXACTLY the same
   WhyML as the trusted declaration (emit-diff 0 on the mirror), stop B4 and report.

R2b (generated Why3 clone-refinement conformance units) is OUT of scope for this run (about a week); record it as the
next step. R6 (one composite record) stays research.

## 3. Gate battery (brief rule 5, every rc teed in full)

fidelity; root + pyref byte-diff vs a base worktree at the starting commit (the emitter is not touched, so expect 0/0/0);
mirror emit sweep (MOVED = exactly the files B1 / B3 / B4 change; each OWED whole-file proof is run); planes 61 (+ the
new plane); all ledgers; `\trusted` and `count-trusted-directives` before / after.

## 4. Costed scope (honest)

Gate S + B0 + B1: ~half a day of wall time dominated by the `statements.py` whole-file proof (~2 h 20 m at low priority).
B2: one to two days of careful work in the reviewer's estimate -- this run attempts it inside the executor's box; if the
box ends first, B0 + B1 land alone (soundness hygiene, \trusted unchanged) and B2-B4 are the recorded next step.
Expected verdict: BROKEN (narrow): -24 (or -18 after B3) markers gross, -3 TCB net, ONLY with B2 green; otherwise
CERTIFIED-BOUNDARY for B4 with B0 + B1 landed.
