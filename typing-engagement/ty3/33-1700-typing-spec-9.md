# 33-1700-typing-spec-9 — TY3 TypeVar/Generic + Whole-Module Monomorphization (DONE)

**Status:** DONE (Gate A APPROVED → core-agent implemented → Gate B green →
Gate C green; one gap doc recorded for the multi-instantiation Module 6
field-mangling edge case, see `33-1700-typing-gap-9.md`).
**Construct:** `TypeVar`/`Generic` (PEP 484 + PEP 695) — the TY3 generic layer.
**Two-plane spec:** `typing-engagement/ty3/typevar-generic-twoplane-spec.md` (Gate A APPROVED).
**Probe:** `typing-engagement/ty3/FEASIBILITY-PROBE.md` — 🟢 GREEN (hand-monomorphized
`Stack[int]` proves 10/10 VCs through the existing pipeline).

## 1. Design

The monomorphization machinery is a new **IR-resolution pass** that runs AFTER
`apply_inline_globals` (the last of the four existing post-Module5 passes in
`frontend/ir_resolve.py:resolve`) and BEFORE Module 6 (WhyML emission). It operates purely
on the resolved IR dict — it does not re-walk the AST. It is total-additive: a module with
NO generics is byte-identical (the pass is a no-op early-return).

### 1.1 Where the type parameters live

PEP 695 `type_params` is on `ClassDef`/`FunctionDef` AST nodes (commit 8335eede parses
them). The IR emitter currently DROPS `type_params`. This DRAFT adds a new optional
TYPE-DECL field `type_params` (list of `{name, bound, kind}`) and a new optional FUNCTION
field `type_params` (same shape), emitted ONLY when non-empty → byte-identical for
non-generic drivers. This is an IR_VERSION bump (1.3 → 1.4, additive).

### 1.2 The pass: `apply_monomorphization(ir_data)`

Located in a new module `frontend/monomorphize.py`, wired into `ir_resolve.resolve` as
step 5 (after `apply_inline_globals`). Steps:

**STEP A — COLLECT.** Walk the resolved IR for instantiation sites: a `Call` whose
`func` is a `Subscript` whose `value` is a `Name` matching a generic class/func decl, OR
an annotation `Subscript` on a generic. Record `(generic_name, concrete_type_str)` pairs.
Also accept the legacy `TypeVar("T")` + `Generic[T]` spelling: a class whose `bases`
contain `Generic[...]` is generic; a `TypeVar` call in module scope declares the var.
Dedupe to the set of (generic, concrete-type) pairs.

**STEP B — DETECT GT4 (polymorphic recursion) and GT3 (ParamSpec/TypeVarTuple).**
- GT3: if any `type_params` entry has `kind != "TypeVar"` → loud-fail
  `PyCSLSemanticError(code="PYCSL-TY3-GT3")`.
- GT4: scan each generic function's body for a `Call` to the same generic with a type
  argument that is NOT in the collected concrete set → loud-fail
  `PyCSLSemanticError(code="PYCSL-TY3-GT4")`.

**STEP C — CHECK BOUNDS (G4).** For each `(generic, concrete_type)` with a bound `B` on
the matching TypeVar, verify the concrete type satisfies `B` (today: exact match or
known-subtype; invariant per GT2). Reject with `PyCSLSemanticError(code="PYCSL-TY3-BOUND")`
if not. Also reject `Any` as a type argument (GT1, `PYCSL-TY3-GT1`).

**STEP D — EMIT.** For each `(generic, concrete_type)` pair, deep-copy the generic's
type_decl and methods, substituting:
- class name `C` → `C_<concrete>` (e.g. `Stack` → `Stack_int`; sanitize non-alnum → `_`);
- the TypeVar name `T` → the concrete type string in every field type, every
  `symbol_table` entry, every `return_annotation`, and every contract clause IR node that
  carries a type (the substitution walks the contract IR recursively, replacing `Name`
  nodes whose `id == T` with the concrete type);
- method names `C__m` → `C_<concrete>__m`;
- `self_type` `C` → `C_<concrete>`.
Then append the specialized decls/functions to the IR, and REWRITE call sites
`Stack[int]()` → `Stack_int()` (the `Subscript`-`Call` becomes a plain `Name`-`Call`) and
annotations `x: Stack[int]` → `x: Stack_int`. The ORIGINAL generic decl + methods are
REMOVED from the IR if they had ≥1 instantiation (they are replaced by the copies); an
un-instantiated generic stays as declaration-only (its method bodies are trusted/no-VC —
the soundness report records it Ignored/GT8).

**STEP E — classify.** Each specialized copy is classified Interpreted in the soundness
report; the un-instantiated generic (if any) is Ignored/GT8; `ParamSpec`/`TypeVarTuple`
rejects are GT3.

### 1.3 What is NOT done (deferred / out of scope)

- **Variance (GT2):** invariant checking only.
- **`ParamSpec`/`TypeVarTuple` interpretation (GT3):** loud-fail, schema-only.
- **`Any` instantiation (GT1):** refused.
- **PEP 695 `type X = ...` alias statement as a generic alias:** the alias is collected
  if it appears in an instantiation; first delivery handles the `class`/`def` forms.
- **Relational/doubled-state E-matching cost probe:** separate probe-agent task; the
  feasibility probe already showed 10/10 VCs for one instantiation.

## 2. Files to change

| File | Change |
|---|---|
| `src/pycsl/ir_schema.py` | `IR_VERSION` 1.3 → 1.4; add `"1.4"` to `ACCEPTED_IR_VERSIONS`; document the `type_params` field. |
| `src/pycsl/frontend/Module5_IREmitter.py` | Emit `type_params` on type_decls/functions when non-empty (additive). |
| `src/pycsl/frontend/monomorphize.py` | NEW — `apply_monomorphization(ir_data)` (COLLECT, GT3/GT4, BOUNDS, EMIT, classify). |
| `src/pycsl/frontend/ir_resolve.py` | Wire `apply_monomorphization` as step 5 in `resolve()`. |
| `src/pycsl/core_ir_semantic.py` | Validate the new `type_params` field shape (additive check). |
| `src/pycsl/Module6_WhyMLTranspiler.py` | No change — the pass produces ordinary monomorphic IR; Module 6 lowers it as today. |
| `docs/ir.md` | §10: document IR 1.4 + the `type_params` field. |
| `docs/pycsl-concrete-syntax-reference.md` | §T-TY3: PEP 695 generic syntax (cites S6). |
| `docs/pycsl-static-semantics-reference.md` | §T-TY3: monomorphization rules, GT2/GT3/GT4 (cites S1). |
| `docs/pycsl-translational-reference.md` | §T-TY3: COLLECT/EMIT lowering (cites the overview §4.1). |
| `test-suite/annotations.md` | Canonical entry for `type_params` / generics. |
| `src/pycsl_lib/typing/...` | Shim: `TypeVar`/`Generic` runtime objects (R1/R2) — identity, no check. |

## 3. Gates

- **Gate B:** `os` SUCCESS, `formal_os_pure` SUCCESS, `bin/doc-coherency.py --check`
  green, byte-identical emission for non-generic drivers (the IR 1.4 bump is additive —
  `type_params` is absent on non-generic drivers, so old drivers stay byte-identical; the
  IR-conformance goldens that DO use generics are refreshed).
- **Gate C (conformance-agent):** S5 subset (§1.7 of the two-plane spec) + S4 shim drivers;
  the no-blend trap (D1) — an un-instantiated generic must NOT claim a per-instance theorem;
  GT4 polymorphic recursion must LOUD-FAIL; GT3 `ParamSpec` must LOUD-FAIL.

## 4. IR shape (1.4, additive)

```json
// type_decl (generic class) — the NEW optional field:
{
  "kind": "record",
  "name": "Stack",
  "fields": [...],
  "type_params": [{"name": "T", "bound": null, "kind": "TypeVar"}]
}
// function (generic method/func) — the NEW optional field:
{
  "name": "stack__push",
  ...
  "type_params": [{"name": "T", "bound": null, "kind": "TypeVar"}]
}
```
Absent on non-generic decls → byte-identical for unaffected drivers (the IR_VERSION bump is
additive per docs/ir.md §10).
