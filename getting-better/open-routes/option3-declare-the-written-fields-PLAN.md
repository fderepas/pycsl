# OPTION 3 — DECLARE THE WRITTEN FIELDS ON THEIR CLASSES (executable plan for gen #34)

**This is ladder item 1 for gen #34.** It is the ONLY state that drives BOTH frame ratchets to zero
(lesson (f5)), and its obstacle is COST/SCALE, which by §A.3 is explicitly **not a floor**.

## WHY IT IS THE ONLY ADMISSIBLE OPTION

Three were on the table:

1. **Keep the honest clauses, move `MAX_TRAP` 2989 → 3000 with its cause.** **RULED OUT.** The
   contract says *never re-baseline a ratchet to make a gate green; if a gate goes red the repair is at
   fault, REVERT* — and `MAX_TRAP = 2989` carries **"may only SHRINK"** in its own declaration. A good
   cause is exactly what makes re-baselining feel earned, which is why the rule exists.
2. **Revert, leave the eighteen clauses dishonest.** Admissible, and what gen #33 did to end clean —
   but it is a COST/SCALE deferral, not a boundary, so it is not where this should stop.
3. **Declare the fields on their classes too.** Then each field enters the emitted RECORD, the `writes`
   clause actually names it, and NEITHER plane counts it. **Both TRAPs go to zero.**

## THE MEASURED BILL — AND IT IS FAR CHEAPER THAN GEN #33 PREDICTED

Gen #33 predicted **20-40 of 53** mirrors moving, including the three slow ones, i.e. ~7 h of proving.
**That prediction was WRONG, and wrong in the cheap direction.** Measured with
`bin/mirror-emit-sweep.sh` against a worktree baseline, with the 14 unambiguous declarations applied:

    MOVERS: 3 of 53
      Module6_WhyMLTranspiler.mlw
      module6_whyml__statements.mlw
      module6_whyml__types.mlw

**`pure_ast`, `expressions` and `functions` DO NOT MOVE** — the three most expensive mirrors in the
tree are untouched. Known proof cost (gen #32's measurements): `statements.py` **2 h 19 m**;
`types.py` and `Module6_WhyMLTranspiler.py` are **UNMEASURED** but are far smaller files. So the
realistic bill for the 14 clear fields is **~3 h of proving**, not 7-25 h.

**RE-MEASURE THIS BEFORE BUILDING** — it was taken with 14 of 18 fields, and adding the three deferred
ones (below) would very likely pull `expressions.mlw` (2 h 21 m) and its importers into the mover set.

## THE FIFTEEN FIELDS TO DECLARE (14 applied in the measurement, 1 already honest)

Types are taken from the LIVE initialisers, not guessed:

| mirror file | class | field | type |
|---|---|---|---|
| `frontend/Module3_Weaver.py` | `PyCSLWeaver` | `_csl_bound_names` | `Set[str]` |
| `frontend/Module3_Weaver.py` | `PyCSLWeaver` | `_csl_star_import` | `bool` |
| `frontend/Module5_IREmitter.py` | `PyCSLToJSONEmitter` | `_m5_dc_unknown` | `List[str]` |
| `frontend/Module5_IREmitter.py` | `PyCSLToJSONEmitter` | `_globals_lookup_funcs` | `Set[str]` |
| `module6_whyml/functions.py` | `FunctionEmissionMixin` | `_erased_truthy_locals` | `Dict[str, str]` |
| `module6_whyml/functions.py` | `FunctionEmissionMixin` | `_fold_unsafe_elems` | `Set[str]` |
| `module6_whyml/functions.py` | `FunctionEmissionMixin` | `_fold_unsafe_sizes` | `Set[str]` |
| `module6_whyml/functions.py` | `FunctionEmissionMixin` | `_loop_targets_read_outside` | `Set[str]` |
| `module6_whyml/functions.py` | `FunctionEmissionMixin` | `_r51_bound_names` | `Set[str]` |
| `module6_whyml/functions.py` | `FunctionEmissionMixin` | `_rebound_collections` | `Set[str]` |
| `module6_whyml/preamble.py` | `PreambleEmissionMixin` | `_emitted_record_field_types` | `Dict[str, str]` |
| `module6_whyml/statements.py` | `StatementEmissionMixin` | `_literal_rebind_lens` | `Dict[str, int]` |
| `module6_whyml/statements.py` | `StatementEmissionMixin` | `_literal_rebind_targets` | `Set[str]` |
| `module6_whyml/types.py` | `TypeInferenceMixin` | `_rebound_collections` | `Set[str]` |

`preamble.py::_formal_params` is in the clause repair but was **not** given a declaration in the
measurement — `= list(params)` is a rebind of a parameter-derived list and wants a type decision, so
treat it as a fourth deferred field rather than assuming `List[str]`.

## THE THREE FIELDS DELIBERATELY NOT TOUCHED — EACH NEEDS A JUDGEMENT, NOT A TYPE

**Do not annotate these by pattern-matching the initialiser.** Each is a real decision:

* **`expressions.py::ExpressionEmissionMixin.ir`** — the TRAP row is a CONTAINER MUTATION
  (`self.ir[...] = …`), not a rebind, and `ir` is the whole IR mapping. Declaring `ir` as a record
  field would put the entire IR into the emitted record of the most widely imported mixin in the tree.
  **Decide first whether `ir` is a record field at all**; if it is not, the honest fix is to stop
  counting a mutation through it as a frame write, which is a change to the PLANE, not to the mirror.
* **`expressions.py::ExpressionEmissionMixin._r188_stub_names`** — initialised `= _map188`, i.e. from
  another map whose own type has to be established first. A guessed `Dict[str, str]` would be a
  fabricated witness value, which is precisely the shape lesson *"a completeness fix that supplies a
  WITNESS value is a soundness route waiting to happen"* warns about.
* **`expressions.py::ExpressionEmissionMixin._r55_subsumed_name`** — initialised `= None`, so it is an
  `Optional[...]`, and route #227 is the standing reminder that an `Optional` in the value model is
  where the `None`-vs-opaque-`int` falsehoods live. It needs the Optional treatment, not a bare type.

All three are in `expressions.py`, which is also the 2 h 21 m mirror. **Landing the 14/15 clear ones
FIRST and the three separately is the right split** — it keeps the cheap, measured part off the
expensive mirror.

## THE GATE IT MUST PASS (M1 discipline — the byte-diff WILL be non-zero)

    1. mirror byte-diff        the diff is EXACTLY the intended record additions and the `writes`
                              clauses that follow from them -- inspected line by line, nothing
                              incidental. Declare every mover by name.
    2. whole-file proof        EVERY mover re-proves 0 non-Valid. Measured set is 3; RE-MEASURE, and
                              run it DETACHED under setsid with an `rc` file (lesson (m4): the rc is
                              the only thing that says it finished).
    3. both frame planes       PREDICT BOTH, then read both:
                                 check-assigns-underdeclaration      TRAP 0    / HOLE 0
                                 check-assigns-writes-survival       TRAP < 2989 / HOLE 0
                              The second is the POINT of the change. If it does not FALL, the change
                              did not do what it was for.
    4. HOLE stays 0            the fields become MENTIONABLE once they are in the record, so this is
                              the leg that actually needs thought rather than confirmation.
    5. corpus byte-diff        predicted 0 MOVED both corpora (these are mirror-only class decls), and
                              the ledgers of lesson (d5) pre-checked, not discovered.
    6. fidelity + field parity `check-self-annotate-sync.sh`, `self-annotate-mirror-check.sh` and
                              `check-mirror-field-parity.py` were all GREEN with the 14 applied --
                              adding a mirror class declaration is sanctioned (gen #32 did it for #63).

## THE HALF-LANDED PATCH

`getting-better/interrupted/2026-09-29-gen33-option3-half-landed.patch` — the 18 honest clauses PLUS
the 14 class declarations, 7 files, 23 insertions. **It has passed NO battery.** Treat it as a HINT and
re-measure from scratch; gen #33 reverted it deliberately, because landing half of option 3 is what
created the ratchet conflict in the first place.
