# OPEN ROUTE #583 — `.value` OF AN `ast.Attribute`-TESTED emit_ir VALUE IS LOWERED TO `svalue_of`, THE SUBSCRIPT PROJECTOR (`IrOther ""` ON AN IrAttr), SO THE MODEL DECIDES `isinstance(x.value, ast.Name)` / `x.value.id == ...` FALSE WHERE CPYTHON TAKES THE BRANCH
**Status: REPAIRED (driver run #6, executor u37 off 8c6b864fa, branch run6-u37, commits a5b292575 (repair) + 3efe30709 (re-conversions) + the docs commit; annotations §7.583). Mechanism: `expressions.py::_handle_attribute_expr` lowers `.value` on an emit_ir value (no handler-scoped projector) to the unified `avalue_of` (IrAttr -> object, IrSub -> value) instead of the Subscript-only `svalue_of`; inline, no new def / projector / axiom. Witnesses: 6 false proofs at base (route exemplar + a01/a02/a03/a04/a10) are NOT PROVED at HEAD, 2 controls PROVE; corpus 9430-9435 (FAIL) / 9440-9441 (PASS). Movers: corpus 9310 / 9311 (re-proved PASS); mirror Module5_IREmitter (whole-file: see REPAIR) and module6_whyml/expressions (7 lines, OWED); `_collect_final_registry` / `_union_arm_tag` VERIFIED again. Three same-class findings (F1-F3) remain open, below.** Opened as: Status: OPEN, PRE-EXISTING (present at run6-int54 c914766a6, before capability R1). Severity 1 (a false claim is a theorem of the model). Found by driver run #6 executor lvL while converting the capability-R1 Module5 functions; opened on the driver's instruction.**

## Mechanism
- `expressions.py::_handle_attribute_expr`, the emit_ir branch (gated on `@mutable_state` / a tparam collector):
  `.value` is not in `_EMIT_IR_STR_ATTRS`, `_EMIT_IR_NODE_ATTRS` or (outside `_py_stmt_augassign`, whose scoped entry
  uses the unified `avalue_of`) `_EMIT_IR_HANDLER_ATTR_PROJ`, so it falls to the default `(svalue_of <recv>)`; the
  reflection table `_EMIT_IR_PROJ` maps `"value"` to `svalue_of` too.
- `svalue_of` (preamble, emit_ir theory) is `match e with IrSub v _ -> v | _ -> IrOther ""`: the SUBSCRIPT value. On
  an `ast.Attribute` (an IR class, `_AST_CLASS_TO_IR_KIND["Attribute"] = "Attribute"`, modelled `IrAttr o a`) the
  Python `.value` is the OBJECT `o` (`object_of` / `avalue_of` read it), but the model reads `IrOther ""`.
- Hence after `isinstance(x, ast.Attribute)` (`is_attribute x`), `isinstance(x.value, ast.Name)` lowers to
  `is_var (svalue_of x)` = `is_var (IrOther "")` = false, and `x.value.id` to `name_of (IrOther "")` = `""`. The
  model decides the branch impossible; CPython takes it for `self.a`.

## Witness (user program)
`witnesses-r583/w583_attr_value_svalue.py`: `if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name): if
x.value.id == "self": return 1` / `return 0` under `ensures \result == 0`. CPython `Em().f(<self.a>)` returns 1.
MEASURED: default model `Verification SUCCESS` (a false claim PROVED) at base c914766a6 (lvL spike,
`witnesses-r1/results/proof.base.p01.log`) and at the lvL head (see EVIDENCE). So this is a false proof, not only a
vacuity gap.

## Where it bites in the mirror
`frontend/Module5_IREmitter.py::_collect_final_registry`, the `self.<attr>: Final[T]` branch (`isinstance(sub.target,
ast.Attribute) and isinstance(sub.target.value, ast.Name) and sub.target.value.id == "self"`): a `#@ assert 1 == 2`
injected there is PROVED (lvL `mres/mutself.log`), so a conversion of that function is vacuous on that path; it stays
`\trusted` (driver decision, run #6). Any other converted function reading `.value` on an Attribute-tested emit_ir
receiver has the same dead path (lvL checked the five R1 conversions: see the run #6 lvL report).

## Repair direction (not built)
Lower `.value` on an emit_ir receiver with the unified `avalue_of` (IrAttr -> object, IrSub -> value) everywhere, as
`_py_stmt_augassign` already does -- or decide by the receiver's tested class; it moves every emission that reads
`.value` on emit_ir (mirror re-proofs owed) and must keep the Subscript path byte-identical where only IrSub is possible.

## EVIDENCE
- `witnesses-r583/w583_attr_value_svalue.py` (CPython: 1 for `self.a`, contract `\result == 0`): default model
  Verification SUCCESS at base c914766a6 AND at the lvL head (191f0624c + docs) -- a FALSE PROOF, not only a vacuity
  gap. typed / store: L3 `unbound type symbol 'array'` (the pre-existing emit_ir gap of those models), so the false
  proof is the default model's. Front end x hoare: EMITTED (no refusal).
- Mirror: `#@ assert 1 == 2` injected in `_collect_final_registry`'s `self.<attr>` branch PROVED (4/4 Valid) and in
  `_union_arm_tag`'s `ast.expr` / `ast.stmt` / `ast.AST` arm PROVED, i.e. both branches are dead in the model; the lvL
  leaf-reachability run (`witnesses-r1/results/leaf-reachability.txt`, one assertion per leaf block, 30 blocks of the
  five R1 conversions) found no other dead leaf. Both functions stay `\trusted` (driver decision).

## REPAIR (driver run #6, executor u37, base 8c6b864fa = int54 + lvM + lvN + lvL, branch run6-u37)

- RULE (annotations §7.583): `expressions.py::_handle_attribute_expr`, the emit_ir branch: `.value` with no
  handler-scoped projector lowers to the UNIFIED `avalue_of` (`IrAttr o _ -> o | IrSub v _ -> v | _ -> IrOther ""`,
  already in the theory, already used by `_py_stmt_augassign`), not the Subscript-only `svalue_of`. It agrees with
  `svalue_of` on every node that is not an IrAttr, so every Subscript read keeps its meaning (`_to_bool`'s
  always-present sub-node prefixes gain `avalue_of`). Inline, no new def, no new projector / theory line, no axiom;
  both live methods' mirror twins are `\trusted`.
- CLASS CHECK (every `.value`-reading site of an emit_ir receiver): `_handle_attribute_expr` default -- FIXED (the only
  attribute-view site that can see an IrAttr); `_py_stmt_augassign` scoped `avalue_of` -- already faithful;
  `_classify_literal_value` scoped `const_pyval_of` / the `isinstance(<x>.value, (int, float))` and `int(v.value)`
  const recognizers -- Constant-only, faithful; keyword `.value` (`kw_value_of`) and the `for a in x.args` element
  (int-erased `get_value`) -- opaque, no false proof (measured a07 / a08 NOT PROVED); `functions.py` SArraySet
  recognizer `svalue_of tgt` -- guarded by `is_sub`, faithful; `ir_resolve` `avalue_of` -- faithful;
  `_EMIT_IR_PROJ["value"]` (the DICT view `.get("value")`) -- see FINDINGS.
- WITNESSES (default model; `witnesses-r583/u37/`, CPython runs each `__main__` and breaks the claim):
  | witness | base 8c6b864fa | HEAD |
  |---|---|---|
  | w583 route exemplar (`x.value.id == "self"`) | PROVED (false) | NOT PROVED |
  | a01 `isinstance(x.value, ast.Attribute)` on Attribute | PROVED (false) | NOT PROVED |
  | a02 Subscript of Attribute, `x.value.value` | PROVED (false) | NOT PROVED |
  | a03 Attribute object none of Name/Attribute/Subscript/Call | PROVED (false) | NOT PROVED |
  | a04 `isinstance(x.value, ast.Call)` on Attribute | PROVED (false) | NOT PROVED |
  | a10 `x.value.id != ""` on Attribute | PROVED (false) | NOT PROVED |
  | a06 Constant `x.value == 5` | L3 type error | L3 type error (unchanged) |
  | a07 call-arg element / a08 keyword value / a09 Starred (opaque reads) | NOT PROVED | NOT PROVED |
  | b01-b05 `pyast_stmt` module-body shapes (incl. the `_collect_final_registry` shape) | L3 `unbound type symbol 'option'` | same (pre-existing gap of user programs with a module-body stmt loop; the mirror carries the type) |
  | c01 / c02 controls (honest bounds through Attribute.value / Subscript.value) | PROVED | PROVED |
  | c03 control, stmt shape | L3 `option` | L3 `option` |
  typed / store (w583, c01): L3 `unbound type symbol 'array'` at HEAD as at base (the pre-existing emit_ir gap of
  those models). Front end: no refusal added.
- CORPUS: 9430-9435 (expected FAIL, NOT PROVED at HEAD: postcondition of `em__f` Timeout, no type error) and
  9440 / 9441 (controls, PASS; not trivially discharged: two-sided bounds, several returns).
- BYTE-DIFF (own base sweep at 8c6b864fa, `bin/byte-diff-compare.py` once root, once pyref, `--new-source` the 8 new
  IDs): root 2 MOVED -- 9310_r1_ctl_constant_subscript_admitted / 9311_r1_ctl_tparam_classdef_admitted, each diff
  exactly `svalue_of` -> `avalue_of` under `is_sub` (M1: both re-proved, PASS); 5 GONE (1798, 4280-4283) and pyref
  13 MOVED / 6 GONE (all `stdlib/json*`) are a sweep-CWD artifact (relative `--import-path` flags / json resolution
  depend on the cwd; the base sweep ran from a scratch dir): re-emitted from each tree's root, base and HEAD are
  identical (5/5 refused alike; json 27/27 identical, the same 6 refused).
- MIRROR SWEEP (vs own base at 8c6b864fa): 2 MOVED. `frontend/Module5_IREmitter.py` (20 lines `svalue_of` ->
  `avalue_of`, all under `is_sub`, plus the two re-conversions) -- whole-file proof below.
  `module6_whyml/expressions.py` (7 lines in `_slice_array_or_opaque` / `_handle_slice_access_expr`, `node.value`
  on a SliceAccess node: `IrOther ""` under both projectors, semantics unchanged) -- whole-file proof OWED (driver);
  `--fun expressionemissionmixin___slice_array_or_opaque --fun expressionemissionmixin___handle_slice_access_expr`
  (`--no-check-vacuity`, proof phase only): rc 0, 2968 Valid / 0 non-Valid. statements / stmt_control_flow / functions /
  Module6_WhyMLTranspiler / frontend/pure_ast emissions UNCHANGED. Keeping expressions.py byte-identical is not
  possible without an exception for those handlers' receivers, which the model cannot justify: the projector choice
  cannot depend on an `isinstance` test, since an untested `"ExprIR"` receiver may be an IrAttr too.
- WHOLE-FILE `frontend/Module5_IREmitter.py` (HEAD, PYTHON_CPU_COUNT=4, HEAVY_LOW): PENDING at the docs commit (queued behind the driver's statements.py proof in the LOW slot); result recorded in the executor report.
- RE-CONVERSIONS (commit 3efe30709): `Module5_IREmitter.py` `_collect_final_registry` and `_union_arm_tag` restored to
  their verbatim live bodies (lvL's 2c7ec1846 state; check-self-annotate-sync: 958 un-trusted mirror functions
  verbatim). `--fun pycsltojsonemitter___collect_final_registry --fun pycsltojsonemitter___union_arm_tag`
  (PYTHON_CPU_COUNT=4, timeout 14400, run to completion incl. the vacuity phase): rc 0, 975 Valid / 0 non-Valid, no
  "could not be checked" line; the same run against the BASE emitter (control): rc 0, 975 Valid / 0, no such line
  either (the conversion proved at base too -- through the dead branch, which is why the leaf check is the gate).
  An earlier pair of runs with timeout 3000 was killed in the vacuity phase (rc 124) and is VOID. Leaf reachability
  (lvL's `leafs.py`, `#@ assert 1 == 2` at the first statement of each of the 15 leaf blocks, `--no-check-vacuity`):
  15/15 NOT proved, including the `self.<attr>: Final[T]` branch (base: 4/4 sub-goals Valid; now 3 Valid + 1
  Timeout, i.e. reachable) and the `ast.expr` / `ast.stmt` / `ast.AST` arm (base: Valid; now Timeout). oom_kill 75
  before and after every proof of this repair (no void run).
  Mirror `#@ \trusted` markers 368 -> 366; trusted-reasons.tsv -2 rows.
- PLANES on HEAD 3efe30709: fidelity (check-self-annotate-sync, self-annotate-mirror-check, doc-coherency --check)
  rc 0; run-soundness-planes.sh (fast + conversion tier, 62 planes) rc 0; check-vacuous-drivers rc 0;
  check-assigns-writes-survival rc 0 (HOLE 0, TRAP 1398 / ratchet 1399); check-trusted-frame-honesty rc 0 (trusted
  0/1, converted 0/63); check-getattr-erasure rc 0; check-trusted-termination-honesty rc 0 (55, ratchet 56);
  check-claim-vacuity rc 0 (1791 at ceiling); check-open-route-carriers rc 0; check-refusal-advice-audited rc 0 (no
  refusal added). Proof-axiom ledger 3 (no axiom).

## FINDINGS (same defect class, measured, NOT repaired here -- each a false proof in the default model at base AND HEAD)
- F1 DICT VIEW `.get("value")` on a node whose `.value` is not the Subscript one: `_EMIT_IR_PROJ["value"]` /
  the `.get("value", {})` site read `svalue_of` (`IrOther ""` on `IrStarred` / `IrNamedExpr` / `IrSliceAccess` /
  `IrMapSet`), so after `x.get("type") == "Starred"` the read value's kind is never `"Var"`: witnesses
  `u37/d01_dict_starred_value`, `d02_dict_mapset_value`, `d03_dict_sliceaccess_value`, `d04_dict_namedexpr_value`
  PROVE `\result == 0` (CPython 1); control `d05_dict_subscript_value` NOT PROVED. (An Attribute wire dict has no
  `"value"` key, so `avalue_of` is NOT the fix there; a dict-view projector over the value-carrying ctors is.)
- F2 `.slice` on an emit_ir value outside the handler-scoped entries falls to the `svalue_of` catch-all (the
  Subscript VALUE, not the index): `u37/a05_slice_default` (`isinstance(x.value, ast.Name) and not
  isinstance(x.slice, ast.Name)` after `isinstance(x, ast.Subscript)`) PROVES `\result == 0`; CPython `a[0]` -> 1.
  More generally every attribute not in a projector table reads `svalue_of`.
- F3 `.value` of a `pyast_stmt` whose class the model does not carry (`ast.Expr` / `ast.Return` / `ast.AugAssign`:
  `stmt_value PSOther` = `IrOther ""`): `u37/b04_expr_value_call` -- NOT MEASURABLE in a user program today (every
  module-body stmt-loop program fails L3 `unbound type symbol 'option'`, b01-b05 / c03, base and HEAD alike); the
  mirror shape is open.
