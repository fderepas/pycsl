**IR well-formedness** is the predicate capturing Module 5's
JSON IR output shape: the structural invariants every
`program_ir` / `function_ir` / `contract_ir` value must satisfy
before Module 6 will accept it.

Two implementations of the same predicate exist, one Python
and one formal, with a machine-checked correspondence between
them.

---

## Python side — `src/pycsl/ir_schema.py:validate_ir`

The Python predicate is `validate_ir(ir_data: dict) -> None`.
It raises `PyCSLIRError` on shape drift. The schema covers:

- Top-level `ProgramIR` shape: `module_name`, `functions`,
  `classes`, `imports`.
- Per-function `FunctionIR` shape: `name`, `params`, `body`,
  `contracts`, `symbol_table`, `return_type`.
- Per-contract `ContractsIR` shape: `requires`, `ensures`,
  `assigns`, `raises`, `variant`, `no_exception`,
  `function_variants`, plus the various `loop_*` and
  `class_*` keys.
- Statement nodes: every `stmt` field with the right
  per-tag (`Assign`, `AugAssign`, `If`, `While`, `For`,
  `Return`, `Raise`, `Try`, `Critical`, `GhostAssign`,
  `TupleUnpack`, `FieldAssign`, `FieldAugAssign`, `Break`,
  `Continue`, `Pass`, `Label`, `Expr`, `Assert`).
- Expression nodes: every `type` field with the right
  shape (`Number`, `Var`, `BinOp`, `UnaryOp`, `Call`,
  `Subscript`, `IfExpr`, `BoolLit`, `Tuple`, `MkTuple`,
  `Fst`/`Snd`/`Proj`, `FieldGet`, …).

`validate_ir` is called once after Module 5 emits, before the
output reaches Module 6 (`src/pycsl/pycsl.py:617` in
`_run_pipeline`). A well-formedness failure is a Module 5 bug
caught upstream of the WhyML emission.

## Formal side — `Phase1c_ValidateIr.v`

The Rocq predicate `validate_ir : json_value → bool` mirrors
the Python predicate over `json_value`s parsed by Q4 U.1's
`Phase0_IrJson.v`. Three bool predicates plus a refinement:

- `validate_ir : json_value → bool` — total boolean
  validator.
- `WellFormedIR : json_value → Prop` — structural propositional
  predicate (matches the dict-shape rules).
- `KeysUniqueRec : json_value → Prop` — recursive
  uniqueness predicate (every object's keys are distinct,
  recursively).
- `well_formed_and_unique_implies_validate :
    forall j, WellFormedIR j /\ KeysUniqueRec j → validate_ir j = true`
  — the soundness arrow.

The full bidirectional correspondence (`validate_ir j = true
↔ WellFormedIR j /\ KeysUniqueRec j`) is U.3 in
`closer-to-code.md` (status doc item 46).

## Correspondence with the Python side

Q4 U.3's theorem captures the Python `validate_ir`'s
semantics as a Rocq predicate. Practically:

1. Python `validate_ir(ir_data)` either returns `None`
   (well-formed) or raises `PyCSLIRError`.
2. Rocq `validate_ir(j) : bool` returns `true` iff `j` would
   pass the Python check.
3. The U.3 theorem establishes the correspondence: the
   formal predicate captures every constraint Python's
   `validate_ir` enforces.

This makes IR well-formedness a *machine-checked spec* for
the Python function — Python's `validate_ir` is the
operational implementation, Rocq's `validate_ir` is the
formal spec, the U.3 theorem is the bridge.

## Why it matters

IR well-formedness is the trust seam (q.v.) between
Modules 1-4 (Python frontend, `\trusted reviewer:` by
design) and Modules 5-6 (Module 5 IR + Module 6
emission + WP calculus, formally proved). A well-formed IR
guarantees Module 6 can emit; a verified `wp_gen_correct`
gives correspondence to the WP calculus; the formal
soundness theorem (`pycsl_soundness`) chains through both.

If the Python frontend (Modules 1-4) produces ill-formed IR,
the issue is caught at `validate_ir` time — before any
WhyML emission. If the Python `validate_ir` differs from the
formal predicate, the U.3 correspondence theorem flags the
gap.

## See also

- [Trust seam](trust-seam.md) — what IR well-formedness
  anchors.
- [Trusted Computing Base](trusted-computing-base.md) —
  where this predicate sits (Tier 0a, machine-checked).
- [Verification condition](verification-condition.md) —
  downstream of well-formedness (Module 6 produces VCs only
  on well-formed IR).
- `src/pycsl/ir_schema.py` — Python implementation.
- `src/formal-semantics/rocq/Phase1c_ValidateIr.v` — formal
  predicate + U.3 theorem.
- `src/formal-semantics/rocq/Phase0_IrJson.v` — the
  `json_value` inductive over which the formal validator
  operates.
- `closer-to-code-execution-status.md` items 26, 39-40, 46 —
  the execution log for the U.1/U.3 work.
