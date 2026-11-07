# FINDING (gen #33, 2026-09-28) — THE FRAME PLANE'S POPULATION IS ONLY `assigns \nothing`, AND 498 METHODS ARE OUTSIDE IT

**Verdict: FAIL-CLOSED, TRAP 18 / HOLE 0 — and it is a MEASUREMENT, not a theorem, which is why it
is now a ratcheted plane with a negative test.**

## HOW IT WAS FOUND: LESSON (a5)'S OWN SWEEP, ON THE DAY (a5) WAS BANKED

Route #228 banked lesson (a5) — *a baseline that records its own follow-up is an open route with a
green gate in front of it* — and prescribed the sweep: grep every gate's baseline/allowlist prose for
a deferred action. Run immediately, it returned four hits:

| hit | verdict |
|---|---|
| `check-collapsed-option-reads.py` — has an `UNPROBED` verdict class and prints "N still OPEN/UNPROBED" | **clean negative.** It reports `0 still OPEN/UNPROBED`; the verdict class is unused. |
| `check-refusal-witness-coverage.py:255` — "…which is why it is RECORDED rather than done here" | **cost/scale, not an undone cheap search** — it states its own price (moves all 437 census messages). |
| `check-trusted-reasons.py:85` — "Recorded as a named follow-up in …" | pointer to a live backlog item; correctly parked. |
| **`check-type-keyed-constant-answers.py:95`** | **LIVE. This document.** |

That last baseline justifies the emit_ir ALWAYS-PRESENT arms (nine sites, seven methods, every one
measured to carry `#@ ensures True`) and then ends:

>>> "THE FRAME HALF IS STILL UNCHECKED and is the named follow-up: a self-field write on the branch
>>> the model DELETES is invisible to the `assigns` proof, because the proof only sees the paths the
>>> model kept."

## THE DEFERRAL-AUDIT RULE IS WHAT TURNED THIS FROM "PROBABLY COVERED" INTO A FINDING

The campaign's rule for a deferral is: **LOCATE the named guard and QUOTE ITS ACTUAL MATCHING RULE.**
`bin/check-trusted-frame-honesty.py` is obviously the guard — its docstring is *about* exactly this
hazard, and states it in fully general terms:

>>> "what it is checked against is the EMITTED body, which is an ERASURE of the live one: the very
>>> calls that do the writing are commonly lowered to effect-free abstract `val`s, so `writes {  }`
>>> can be true of the emission and false of the source."

Reading the DOCSTRING, the follow-up is covered. Reading the CODE, it is not:

    :634   if stripped == "#@ assigns \nothing":  nothing = True
    :637   if (trusted == want_trusted) and nothing:

`_mirror_nothing_stubs` admits a method **only on an exact string match against
`#@ assigns \nothing`.** Both of the plane's populations — trusted (6/76) and converted (63/130) —
are that one spelling. Nothing else is in either arm.

And none of the seven methods the deferral is about declares `\nothing`: `_try_union_is_none_match`
declares `assigns self._in_spec`, and the other six declare between 6 and 20 fields.

>>> **SO THE HOLE IS FAR WIDER THAN THE FOLLOW-UP IT WAS FOUND BY. An UNDER-DECLARED NON-EMPTY
>>> `assigns` IS EXACTLY AS FALSE AS AN UNDER-DECLARED EMPTY ONE, and 498 of the 1279 mirror methods
>>> carrying an `#@ assigns` clause are non-empty — i.e. in neither arm of the only plane that looks
>>> at frames against the LIVE source.**

This is the campaign's own rule turned on its best frame instrument: *a guard whose population is
`assigns \nothing` has checked nothing about a non-empty `assigns`* — and the docstring's generality
is precisely what makes the scope invisible, because it describes the HAZARD in full while the code
implements one case of it.

## THE MEASUREMENT

`bin/check-assigns-underdeclaration.py`. For every mirror method with a non-empty `#@ assigns`, the
DIRECT `self.<f>` writes of its live twin in the same class. **Direct only — no call graph — so every
row is a LOWER BOUND and unarguable.**

    non-empty `#@ assigns` clauses            498   (of 1279 with any clause)
    TRAP  (live write omitted from the clause)  18   field-occurrences, 9 methods
    HOLE  (and the field is class-DECLARED)      0

**All nine methods are `\trusted`** — the population whose contract is ASSUMED and never checked, so
this is not a cosmetic count. 17 rebinds and one container-mutation (`self.ir[...] = …`).

    Module3_Weaver.py      PyCSLWeaver             visit_Module                _csl_bound_names, _csl_star_import
    Module5_IREmitter.py   PyCSLToJSONEmitter      visit_Module                _globals_lookup_funcs
    Module5_IREmitter.py   PyCSLToJSONEmitter      _collect_class_fields       _m5_dc_unknown
    expressions.py         ExpressionEmissionMixin _handle_binop               _r55_subsumed_name
    expressions.py         ExpressionEmissionMixin _handle_dotted_call         _r188_stub_names, ir (mutate)
    functions.py           FunctionEmissionMixin   _reset_function_state       _erased_truthy_locals, _fold_unsafe_elems,
                                                                               _fold_unsafe_sizes, _loop_targets_read_outside,
                                                                               _r51_bound_names, _rebound_collections
    preamble.py            PreambleEmissionMixin   _emit_type_decls            _emitted_record_field_types, _formal_params
    statements.py          StatementEmissionMixin  _emit_body_code             _literal_rebind_lens, _literal_rebind_targets
    types.py               TypeInferenceMixin      _track_collection_metadata  _rebound_collections

## WHY IT IS FAIL-CLOSED, AND THE DISCRIMINATOR IS GEN #32'S, NOT A NEW ONE

**Every one of the 18 omitted fields is UNDECLARED in its mirror class.** Module 6 builds a class's
record from the fields the class DECLARES, so an undeclared field is absent from the record, hence
**unmentionable** — no caller can state, let alone prove, anything about it. The `assigns` is
dishonest to a human reader and claims nothing false to the model.

That is the same cause and the same exact coextension gen #32 measured **from the opposite
direction** in `check-assigns-writes-survival` (TRAP 2989 / HOLE 0): there, a field NAMED in an
`#@ assigns` but never DECLARED is silently dropped from the emitted `writes`. The two planes now
bracket the frame:

    gen #32   declared-but-not-emitted   `#@ assigns` names it, the emitted `writes` drops it
    gen #33   written-but-not-declared   the live body writes it, the `#@ assigns` omits it

and both bottom out in the same question — *is the field in the record?* — with the same answer
today. **Because they share a cause, they will stop being coextensive together**, which is the real
reason both HOLE arms must stay ratcheted and negative-tested rather than argued.

## THE INSTRUMENT IS CONTROLLED IN BOTH DIRECTIONS

* **Positive control** (the probe can see an omission): a synthetic mirror/live pair where `C.f`
  declares `assigns self._a` and writes `self._a` and `self._b`, and sibling `C.g` declares both.
  The probe flags `f` and does NOT flag `g` — so it discriminates, rather than flagging everything.
* **HOLE negative test** (`--self-test`): declare one measured-TRAP field in its own mirror class and
  require HOLE to fire. It does (`_csl_bound_names` in `PyCSLWeaver` → HOLE 1). Without this leg,
  `HOLE 0` would be indistinguishable from a dead arm — which is the exact failure route #94 taught
  and which gen #32 guarded the same way.
* The "declared" set is **deliberately OVER-approximated** (every class-level annotation in the file,
  plus in-file bases), so HOLE errs toward FIRING.

## WHAT IS NOT CLOSED

* **The call graph.** Direct writes only. `check-trusted-frame-honesty` already has a transitive
  fixpoint with table-aware dispatch; pointing it at the non-empty population is the obvious next
  increment and would raise TRAP, not HOLE, unless a transitively-written field is class-declared.
  **That is the one way HOLE could become non-zero without any source change**, so it is the next
  measurement, not a nicety.
* **Correcting the 18 clauses.** Each is a one-line `#@ assigns` edit on a `\trusted` stub. Cheap,
  but it changes the emitted `writes` of the stub's abstract `val` in every importing mirror, so it
  owes the re-proof bill lesson (k4) prices. TRAP is a ceiling that should come DOWN as they land.
