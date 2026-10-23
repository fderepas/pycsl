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

## S-C RESULT (retry, after P1+P2) — BROKEN: `AuditReport.extend` CONVERTED (gen #36)
Built by the retry executor before the 2026-10-12 session death; RE-VALIDATED FROM SCRATCH on
2026-10-13 by the driver (pre-crash gate results discarded): inline arm in
`statements.py::_handle_expr_stmt` (`self.f <- Array.append self.f <src>` for list self fields whose
element type maps exactly to the emitted array element; everything else keeps the refusal) + record
param actuals typed as the record in `expressions.py`. Witnesses 1945 PASS / 1946 FAIL (non-vacuity)
/ 1947 PASS (caller) / 1948 FAIL (array-int record element refused) / 1949 FAIL (self-alias rejected
by Why3 "illegal alias"); 0980/0981 unchanged (refused). Corpus 0 MOVED / 1410 (4 new), pyref 0 /
2199; mirror 2 MOVED (audit_proof: 3 `Array.append`, whole-file 48 Valid / 0; pycsl: the imported
val gains the three length ensures — whole-file re-proof queued); fidelity 898 verbatim; fast planes
61/61. Count 477 -> 476. P3 (`__init__`-assigned field element types) remains for 0981.

## S-A/S-D RESULT (gen #36, ch16, 2026-10-15) — census re-measured; dict/set track STOPPED on a base soundness hole; list `sort` BROKEN (1 marker)
CENSUS @1de9420d (re-measured, not inherited; `getting-better/ipm/ch16/census.py`, table `census-table.txt`): 125 of 432
trusted-reasons rows have a LIVE body calling a listed mutator (24 cross-file sibling stubs
excluded). Each was ported verbatim + live signature in a scratch copy, emitted, and while
the first blocker was an in-place-mutator refusal ONLY that mutator was neutralised
(statement -> `pass`; `x = r.pop()` -> `r[-1]`, `setdefault` -> `get`) and re-emitted.
76 rows have a mutator FIRST blocker (69 then hit another blocker — mostly the int-erasure
seam, nested-closure lift, `with ... as`, by-ref param stores — 3 loop past 15 mutators);
only **4 type-check** once their mutators are neutralised:
  `_Harvester.run` (sort @ self list field), `_inject_functions` (add @ set-comprehension
  local), `_Unparser.write` (extend @ self list field — a recorded certified boundary: its
  honest `assigns self._source` breaks 19 effectful `interleave` callbacks), and
  `_Unparser.visit_Module` (clear @ self dict field).
Rows by mutator x receiver: pop@local 24, extend@local 19, setdefault@local 10,
setdefault@self 9, update@local 8, add@local 6, add@self 5, pop@self 4, sort@local 4,
setdefault@param 4, clear@self 4, update@self 4, others <= 2. The local-list mutators are
the largest population and unblock NOTHING today (every such row's next blocker is the seam).

S-D (dict/set receivers) — STOPPED, not built: probing the alias guard found the MAP carrier
already UNSOUND AT BASE, so any new dict/set mutator arm would extend a hole, and the hole is
cross-method (no per-function syntactic guard can close it). False claims PROVED at
1de9420d (all CPython `True`, claim `\result == False`; reproducers in
`getting-better/ipm/ch16/`):
  * `field_set_alias_local.py` — the review's `stale_dict` in Python form with the EXISTING
    `@mutable_state` set-field `.add` lowering: `a = self.s; self.s.add(1); return 1 in a`.
  * `field_alias1.py` — `self.d = {}; self.g = self.d; self.d[1] = 5; return 1 in self.g`.
  * `field_alias2.py` / `field_alias3.py` — CROSS-METHOD: `link()` does `self.g = self.d`;
    `m()` does `self.d[1] = 5` (dict store) / `self.s.add(1)` (set add) and returns
    `1 in self.g`; `m` proves `\result == False` with no precondition.
  * `repro_param_noop.py` — the `@mutable_state` set-PARAM `.add` no-op
    (`statements.py` "sound no-op" arm): callee `m(s)` does `s.add(1)`, caller
    `s = set(); s.add(2); self.m(s); return 1 in s` proves `\result == False`.
Root cause: dict/set values (locals, fields, params) are pure Why3 maps, so every second
name holds a COPY; route #59's guard sees only local-alias STORES. Arrays are immune
(regions): Why3 rejects a second record field aliasing an array field ("mismatches
regions", `ipm/ch16/sort_spike_fieldalias.mlw`) and region-shared `let`/`ref` aliases see
in-place writes. Reopening capability: a region (by-reference) carrier for dict/set fields,
or a whole-class field-alias refusal + a caller-visible param frame.

S-A' (list `sort` on a self field) — BROKEN. Spike `getting-better/ipm/ch16/sort_weak.mlw`
(`val array_sort_inplace (a: array 'a) : unit writes { a }`, axiom-free, no new theory):
frame/length controls Valid (alt-ergo + z3); positional and Why3-alias false claims Unknown;
a COPY alias proves (f3) -> the emitter arm refuses any function naming the field outside
`len(...)`. Seam 1c99fe5a (witnesses 2260-2267); conversion `_Harvester.run` 459 -> 458.
