# wall-lessons.md — the self-tcb-reduction-driver lesson store

*The Gate S-lesson ledger (per `config/skills/self-tcb-reduction-driver/SKILL.md`). One entry per driver
run/resolved wall. A lesson is written ONLY after its trigger/validity test returns PASS or CARVE-OUT,
with the wall it came from and the `L`-input that revealed the divergence. Over-general lessons are carved
to their valid complement, never kept whole; irreconcilable ones are REJECTED and logged.*

---

## 2026-07-10 — Driver run #1: Gate W discriminated a non-wall (RecordInfoView value-typing)

**Wall-signal (from the base loop):** `_field_type_for`/`_field_type_of`'s value read
`info.get("field_types",{}).get(f)` int-collapses because a `Dict[str, <RecordInfoView TypedDict>]` field
emits `map string (option int)` (opaque value), not `map string (option recordinfoview)`. First surfaced
by the U build (`file-type-of-wall-impl.md` status).

**Gate W cheap-win test (the `L`-input):** read `_m5_get_dict_value_type` (`Module5_IREmitter.py:3688`).
It returns `"string"` for `Dict[str,str]`, `"map int (option ν)"` for `Dict[str,Dict]`, `"seq T"` for
`Dict[str,List]`, and **`return None`** for `Dict[str, <record-name>]` — a MISSING case, not a wall. The
fix is one recognizer branch (if the value annotation is an `ast.Name` naming a declared TypedDict/record,
return its `whyml_name`), analogous to the existing three. **Verdict: NOT A WALL — a bounded recognizer
gap the base loop handles inline. Gate W did NOT escalate** (no report/review/impl cycle spent). This is
the cost-control gate working: the expensive cycle is reserved for walls where a build could be REFUTED,
not routine recognizer additions.

**Lesson (ignore-signal kind → trigger test):**
> Candidate rule: *"a `Dict[str, <TypedDict>]` value that emits opaque `option int` is a wall
> (leave-trusted / needs a review cycle)."*
> **Trigger test (perturb the signal against `L`):** does the opaque emission actually resist a bounded
> fix? Measured NO — `_m5_get_dict_value_type` simply lacks the record-value case; adding it is the same
> shape as its three existing cases. So the "wall" signal is spurious here.
> **VERDICT: CARVE-OUT.** The rule is kept only for value shapes that genuinely resist a recognizer
> (e.g. an iterated map — `_field_type_of`'s `.values()`, the certified map-iteration boundary). For a
> *keyed-read-only* `Dict[str, <declared record/TypedDict>]`, it is NOT a wall — **check for a missing
> `_m5_get_dict_value_type` case before escalating.**

**Carried-forward carve-out (the reusable takeaway):**
> **"opaque `option int` value ≠ wall."** Before escalating a `Dict[str, ν]`-value opaqueness to a wall,
> check whether `ν` is a shape `_m5_get_dict_value_type` already could handle with one more case
> (str / Dict / List / **declared record-or-TypedDict name**). Only a value that must be *enumerated*
> (not just keyed-read) is a genuine map boundary (see `file-type-of-wall.md`). Sibling of the reviewer's
> earlier carve-out *"search-by-value-field ≠ enumerate — check for a missing index before `pydict`."*

**Driver outcome:** no wall escalated this run. The RecordInfoView recognizer is a cheap base-loop item
(part of the scoped `_field_type_for` build, which additionally needs U + §10.4 re-port — a build, not a
wall). The frontier's genuine walls are already resolved: `_field_type_of` full-body map-iteration =
CERTIFIED-BOUNDARY (`file-type-of-wall.md`, S-R2 spike refuted); U mechanism = VALIDATED (a build, not a
wall). Gate W's discrimination — flagging nothing this run — is the calibrated behavior (a driver that
escalates everything, or nothing without measuring, is miscalibrated).

## 2026-07-10 — Driver run #2: FULL cycle fired — Term-rewriter wall = BOUNDED FEATURE (oracle-refuted the boundary)

**Wall-signal:** the `proof2why3/canonical.py` term rewriters (`_flip_comparisons`, `substitute`, …) —
recursive AST tree-REWRITERS that consume an immutable `Term` (9-constructor sum) and CONSTRUCT a
transformed `Term`. Gate W cheap-win test: clearly not cheap (construction + list-child recursion +
termination, well beyond the reader recognizers) AND breakability genuinely UNKNOWN (no converted method
constructs an ADT value). **Gate W ESCALATED** — the full report→fable-review→impl cycle fired.

**The cycle (all four gates exercised):**
- **Report** `term-rewriter-wall.md` — SOTA framing (verified AST-transformation is native proof-assistant
  territory; the question is the SMT/contract setting + the emitter path), 3 suspected fault lines
  (C: construction, L: list-child map, T: termination), 3 costed routes, open question "boundary or bounded?".
- **Gate R (fable review, artifact-teeth)** `term-rewriter-wall-response.md` — an INDEPENDENT fable agent
  (blind to the sub-loop) RAN the oracle: wrote `term-rewriter-spike.mlw` (a `term` variant with fixed-arity
  `Binop` AND list-child `App (list term)`, mutual `size`/`size_list`, the `flip`/`flip_list` rewriter with
  `variant`, the element-decrease as a proved `let rec lemma`) → **6/6 Valid (Alt-Ergo + Z3), 0 axioms**,
  negative control fails (non-vacuous). Verdict: BOUNDED FEATURE. Gate R passed WITH the artifact.
- **driver-verifier (check the claim)** — independently re-proved the spike (6/6 Valid) and CAUGHT-then-cleared
  the "0 axioms" claim: `grep -c axiom` = 5, but all 5 are COMMENTS; `^axiom ` = 0 real declarations →
  ledger-clean confirmed. (The claim survived verification — but the driver checked, it didn't trust.)
- **Gate P impl plan** `term-rewriter-wall-impl.md` — spike-first (the make-or-break already PASSED),
  refutation exit moot (confirmed breakable). Scopes the EMITTER build (T-C1 recursive-constructor emission
  from a dataclass call; T-C2 comprehension→recursive helper; T-C3 list-leg `size` + element-decrease lemma;
  T-C4 term-typed return), with the one open coupling-rule check (a CONSTRUCTED term value may need the
  certificate to cover the constructor eliminator, not just projection).

**Lesson (defer-to-oracle kind → validity test → PASS):**
> **A recursive-ADT tree-REWRITER (construct + list-child map + structural termination) is a BOUNDED
> FEATURE, not a boundary — proven axiom-free by spike.** It sits between the two poles already on record:
> the reader ADT (`emit_ir`, SOLVED — projection only) and the map-values-iteration wall
> (`file-type-of-wall.md`, BOUNDARY). Validity test: the oracle spike genuinely distinguishes the case
> (6/6 Valid, control fails) and sanctions the action (build, don't leave-trusted). PASS.
> **Carry-forward:** before classifying an ADT-transforming method as a boundary, SPIKE the target (variant
> + list-child map + `size_list` measure) — construction and structural termination discharge in Why3
> axiom-free; the real cost is emitter-GENERATION (the M2 gap: target-provable ≠ emitter-generable), a
> build, not a wall.

**Driver outcome:** the wall is BREAKABLE (bounded feature) — NOT a certified boundary. The independent
oracle review overturned the report's uncertainty. Next phase = the emitter build (`term-rewriter-wall-impl.md`
T-C1..C4), spike-gated on T-C1 (emitter-generability, the half the target-spike didn't cover). This run
demonstrates the FULL driver cycle (contrast run #1, where Gate W correctly declined to escalate a non-wall).

## 2026-07-11 — Driver run #3 (AUTONOMOUS, 4h): Phase 1 = no_cheap_remaining; Phase 2 = _field_type_for build
Phase 1 drain: confirmed the cheap-conversion supply is EXHAUSTED (reader byte-0 wins all landed; the last
untested class, the `_collect_*` stmt-walkers, measured NOT cheap — `for s in stmts` over `List[Dict]` +
Set/dict accumulators = a stmt-walker feature gap). → Phase 2. Target: the `_field_type_for` build (all
pieces now scoped: reverse index [validated byte-inert], U [mechanism validated], RecordInfoView recognizer
[bounded — `_m5_get_dict_value_type` + the `_m5_record_class_names` registry], §10.4 re-port of the 2 U-edited
verified methods). Delegated + driver-verifier-gated.
