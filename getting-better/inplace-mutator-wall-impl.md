# W-IPM — implementation plan (from `inplace-mutator-wall.md` + `inplace-mutator-wall-response.md`)

Gate P: spike-first, refutation exits, three-L-plane battery (fidelity, whole-file Why3 of every
moved mirror, corpus + pyref byte-diff — M1 if non-zero), ledger 3, non-vacuity.
Honest payoff (review §6): 1 sure / <=4 realistic / 8 ceiling of 435 stubs. The dominant
cross-cutting blocker is the int-erasure seam, not this wall; build only the R-C pilot now.

## S-C — R-C pilot: `append`/`extend` on a LIST-typed self field of a non-`@mutable_state` class
Lowering: `self.f <- Array.append self.f other` (fresh array, right length) under `writes {self.f}`;
REFUSE (never `_coerce_to_int`) when the field's element type is a record held as `array int` (O7).
Steps, each with its refutation (review §5): (1) corpus-shaped probe `Report.extend` with
`ensures \length(self.passes) == \old(\length(self.passes)) + len(other.passes)` proves — REFUTED if
`len(other.passes)` is an opaque `iter_length` or the arm needs an emitted-file change elsewhere;
(2) non-vacuity twin (`== \old(...)`) NOT proved; (3) corpus 0981 REFUSED->emitted with its false
`\length(self.xs) == 2` NOT proved, 0980 (`reverse@self`) unchanged; (4) byte-diff 0 elsewhere,
`0775`/`0941` identical; (5) mirror: un-trust `AuditReport.extend` (audit_proof.py) with the step-1
postcondition, whole-file proof; plus a caller probe `n = len(r.passes); r.extend(other); return n`;
(6) the `array int` record-element twin REFUSED.
Any refutation -> revert, record CERTIFIED-BOUNDARY (correctness) or COST/SCALE with the blocker.
## S-A (local `pop`) and S-D (dict mutators: alias guard FIRST — `stale_dict` must be refused) are
## deferred until S-C lands; ROI is low (review §6).

## S-C RESULT (gen #36, 2026-10-12) — step 1 REFUTED on COST/SCALE (missing prerequisites), not correctness
The arm itself (`self.f <- Array.append self.f (Array.make 1 v)` / `... o.g`, inline in
`_handle_expr_stmt`, refusing anything whose element type is not exactly the Why3 array type) lowered
correctly, and the hand-repaired model is sound and non-vacuous (`getting-better/ipm/hand.mlw`: the
length postcondition Valid; `hand_nv.mlw` twin Unknown). Three PREREQUISITES are missing:
  P1. a QUOTED forward-reference parameter annotation (`other: "AuditReport"`) is typed `int`
      (`_record_param_classes` empty) — the mirror's exact shape;
  P2. `len(<record-param>.<field>)` emits `iter_length other.passes`, an UNBOUND symbol (L3-tc ✗):
      `_handle_len_call` (expressions.py ~6629-6656) uses `Array.length` only for `self`;
  P3. a list field assigned in `__init__` (corpus 0981) has no recorded element type, so the
      element-type check cannot distinguish `List[int]` from records erased to `array int`.
P1/P2 are int-erasure-seam links (review §6); they are promoted to their own lever (W-IPM-P).
