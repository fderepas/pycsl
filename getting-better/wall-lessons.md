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
