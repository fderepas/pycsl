# set-value-model-wall-impl.md — implementation plan (spike-first; emission-refutation exit)

Synthesized from `set-value-model-wall.md` + `-response.md` (Gate R **CONFIRM**, one mandatory emission rule). The
MODELING is proven (fable `scratchpad/set-oracle.mlw`: `fset string` mem/dedup goals Valid, evil-twin non-vacuous,
ledger-neutral). The impl make-or-break is the EMISSION.

## Design (per the fable mandatory rule)
- A local `s: Set[str] = set()` → an executable `set.SetApp[string]` value (NOT logic-only `set.Fset`/`map.Map`,
  which fail "used in a non-ghost context" in a program `if`). Emit `use set.SetApp with type … string` + a
  decidable program string-equality `val eq (x y: string): bool ensures { result <-> x = y }` (a decidable
  primitive, NOT a project axiom — ledger stays 3).
- `set()` → `SetApp.empty`; `s.add(x)` → `s := SetApp.add x !s`; `x not in s` → `not (SetApp.mem x !s)` (a program
  bool GUARD in the `if`). The spec plane (if ever needed) reasons at `Fset` logic level.
- **CRITICAL RULE:** the recogniser emits the `if not mem` GUARD only — it must NOT put a set-NON-membership fact in
  the contract/an assert (`assert { not (Fset.mem "c" !s) }` times out). The fixed `requires True / ensures True /
  assigns <frame>` shape satisfies this (no non-membership ensures). Verify no such obligation is emitted.
- Gated on a corpus-absent `Set[str]`-local sentinel → the 767 corpus stays byte-identical.

## Gate S — EMISSION make-or-break SPIKE FIRST (refutation exit)
1. Re-prove the fable oracle (`why3 prove -P z3 scratchpad/set-oracle.mlw`) → reproduce Valid + ledger-neutral.
2. Emit the Set[str]-local recogniser (gated on a new `_uses_str_set` signal) + a MINIMAL fixture: a method with a
   `Set[str]` local, `.add(x)`, an `if x not in s:` guard, reading a result. `pycsl <fixture> --keep-mlw`. Does
   `= set()` lower to `SetApp.empty : set string` (NOT `ref 0`), `.add`→`SetApp.add`, `not in`→`not (SetApp.mem …)`
   (program bool, NOT `contains_check (str_hash_op …)`), and TYPECHECK (L3-tc ✓) + the fixture PROVE?
   - PASS → build the recogniser fully.
   - REFUTE (SetApp clone won't emit / the string-eq val forces something / the guard won't type / it can't gate
     byte-inertly) → REVERT ALL, record CERTIFIED-BOUNDARY (§ GATE-S OUTCOME) with the exact Why3/emit error.

## Build (only if Gate S PASSES) — fixture-witness pattern (commit infra + fixture, count unchanged)
(a) preamble/emit: the `set.SetApp[string]` clone + decidable string-eq `val`, gated `_uses_str_set`.
(b) recognisers: `= set()` local → `set string` ref (`_prescan_str_set_locals`); `.add(x)` → `s := SetApp.add x !s`;
    `x in s`/`x not in s` → `SetApp.mem`/`not SetApp.mem` (program bool). No non-membership obligation.
(c) reference fixture `test-suite/corpus/pycsl-reference/0923_str_set_local.<ext>` (git add -f, 0918/0921/0922
    convention): builds a `Set[str]` local, adds, membership-guards, proves faithfully (non-vacuous; evil-twin).
Gate: fixture proves; corpus byte-diff 0 (gated ⇒ inert); ledger 3 (SetApp stdlib, string-eq val is decidable-prim,
no project axiom — verify `_AXIOM_REGISTRY`/allowlist untouched); fidelity 52/52. Count UNCHANGED (infra + fixture
witness — the L4a precedent). NO stub conversion in THIS increment.

## Follow-on (next increment) — converge `_collect_class_fields`
Co-land the Set[str] recogniser + the const-reflection node (isinstance(x,(int,float)) tuple-of-types + int(x)) + the
5 body-faithful helper ports (_m5_get_list_elem_type/_m5_get_field_key_type/_m5_get_option_field_inner/
_is_dataclass_decorated/_cf6_is_cases_list_of_dict) + L4a pyval + R2 ast.walk → convert `_collect_class_fields`
(count 1013→1012). Each residual measured; do them as sub-increments, spike-gated.

## Gate battery (per increment — driver-verifier FRESH)
Fidelity ∧ (whole-file proof OR --fun+wedge-note) ∧ byte-diff-0 (gated) ∧ ledger==3 (no project axiom; SetApp/Fset
are trusted-stdlib) ∧ count (unchanged for infra+fixture; strictly down for a conversion) ∧ non-vacuity (MUTATION
TEST; real SetApp.add/mem, NO str_hash_op/contains_check/int-hash facade; NO non-membership proof obligation).

## Honest costed scope
The Set[str] recogniser (a + b + fixture) is the shared infra increment. The `_collect_class_fields` conversion is
the follow-on (const-reflection + 5 helpers). Refutation exit at Gate S if the SetApp emission walls (the model is
proven; the tool's executable-set emission is the residual risk).

## GATE-S OUTCOME — §_collect_class_fields R7 (2026-07-21, FINAL convergence attempt)

**R7 SPIKE = PASS (BOUNDED).** Tuple-return pyval-seq promotion is a faithful, bounded
tuple-position extension — NOT a from-scratch tuple-value subsystem. Emit evidence
(`scratchpad/r7spike/tup.py`, `-> Tuple[List[Dict[str,PyVal]], Dict[str,int]]`):
- return type emits `(seq pyval, map string (option int))` (NOT `(array int, map int (option int))`);
- `fields.append({"name":"x"})` lowers to
  `fields := Seq.snoc !fields (PMap (map_update_some (const (None: option pyval)) "name" (PStr "x")))`
  — a REAL pyval carrier, NOT `Seq.snoc !fields 0` / `array int`;
- `field_defaults["y"]=3` → `map_update_some !field_defaults "y" 3` (native string key);
- L3-tc ✓ and **proves** (Alt-Ergo→Z3, "All contracts formally proven").

R7 build (4 byte-inert pieces, corpus-absent gates): Module5 `local_list_elem_types`
capture (`List[Dict[str,PyVal]]` local → seq elem "pyval") + `_detect_seq_promotion`
pyval marking; Module6 `_reset_function_state` promotes any `seq pyval` local to
`_pyval_seq_locals`; `_infer_tuple_slot_type` types a pyval-seq slot `seq pyval` and a
string-keyed dict slot `map string (option ν)`; `_uses_pyval` fires on a `seq pyval` local.

**R6 = BUILT (BOUNDED).** The emit_ir ADT already carries `IrListN/IrSetN/IrDictLit`
(kind_of "ArrayLit"/"SetLit"/"DictLit"); only the discriminants were missing. Added
`is_listn`/`is_setn`/`is_dictlit` (definitional over existing ctors, NO axiom) +
`_AST_CLASS_TO_IR_KIND` {Dict/Set/List} + `_KIND_DISCRIMINANT` {DictLit/SetLit/ArrayLit}.
emit_ir theory is @mutable_state-gated → corpus byte-identical.

**R8 = TRIVIAL.** Mirror `_array_init_size` param `rhs: ast.expr` → `"ExprIR"` (1 line).

**R1 = MAPPED BOUNDED (not built).** `for target in stmt.targets` re-derives mechanically
by cloning the existing `_pyast_walk_recv`/`ast_walk` `_classify_iterable` branch:
`val function targets_of (s: pyast_stmt): irlist` + `_pyast_targets_recv` recognizing a
`<pyast_stmt local>.targets` Attribute → loop via `irlen`/`irnth` (the `bases_of` precedent).
No axiom.

**CONVERSION = R7-CERTIFIED-BOUNDARY (NOT converted; reverted clean).** The full verbatim
body port requires the `@dataclass` branch (`not fields and _is_dataclass_decorated(node)`),
which calls **two reflection-heavy helpers that WALL L3-tc**:
`_m5_get_option_field_inner` and `_cf6_is_cases_list_of_dict`. Both use the
`type(x).__name__` / `getattr(x, attr, default)` idiom (+ `_m5_get_option_field_inner`'s
`(class_name, field_name) not in _M5_OPTION_FIELD_ALLOWLIST` frozenset-**tuple**-membership).
The emitter has NO faithful generic lowering for `type(<emit_ir>).__name__` or
`getattr(<emit_ir>, <str>, <default>)`: it INT-ERASES them —
`type(annotation).__name__` → `get___name__ (py_type_1 annotation)` (opaque int hash),
`getattr(annotation, "slice", None)` → `0` — and the resulting mix of an int-typed
`py_type_1` guard against the `emit_ir`-typed `annotation` fails typecheck:

```
File "src/self-annotate/src/frontend/Module5_IREmitter.mlw", line 921:
This expression has type PyCSL_Program.emit_ir, but is expected to have type int
  (in pycsltojsonemitter___cf6_is_cases_list_of_dict — `get___name__ (py_type_1 annotation)`)
```

So the task's premise "port the 5 helpers verbatim (they type-check fine)" is REFUTED for
these two. Converting them needs EITHER a new generic `type(emit_ir).__name__` +
`getattr(emit_ir, str, default)` reflection subsystem (from-scratch, session-scale) OR a
LIVE-tool refactor of both helpers to the `isinstance`-style the emitter already lowers
(a separate byte-diff-0-gated refactor project). Count could NOT go down this increment
(the two helpers can only be added as trusted stubs, which would raise the count).

**Disposition:** R6+R7+R8 are PROVEN/BUILT but have no completed co-target conversion this
increment → dead infra → REVERTED ALL src edits clean (corpus byte-diff 0 preserved,
count unchanged at 1013). Precedent: K1/K4/L3 "capability BUILT+Gate-S PROVEN, NO bounded
co-target → reverted". **The residual wall is NOT R7 (bounded, proven) — it is the
`type()/getattr` reflection helpers in the dataclass branch.** Next attempt must FIRST land
the two-helper front (live isinstance-refactor OR reflection subsystem), THEN co-land
R1+R6+R7+R8 + body port.
