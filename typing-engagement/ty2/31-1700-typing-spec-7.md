# 31-1700-typing-spec-7.md — `@overload` Implementation Spec (DONE, graduated)

**Status:** DONE — graduated to Normative. Coordinator EDITORIAL APPROVED; core-agent
implemented both planes; Gate B (standing gate) GREEN; Gate C (conformance) GREEN
(see `typing-engagement/ty2/conformance_ovl/GATE-C-RESULTS.md`).
**Tier:** TY2 (aggregates and interfaces).
**Construct:** `@overload` (PEP 484).
**Two-plane spec authority:** `typing-engagement/ty2/overload-twoplane-spec.md` (Gate A APPROVED).
**Global guides honoured:** `typing-global-impl.md` §0 (no-blend), §4 (per-construct pipeline + gates),
§5 (TY2: "overload -> a guarded contract family proved against the single implementation"). The
core-agent hard rule: overload is a guarded contract family — multiple `@overload`-decorated stubs
(each with different parameter types + a guarded postcondition) collapsed onto ONE implementation,
the guards selecting which overload's postcondition applies. NO `\trusted`.

**This is a planning document. No `src/pycsl/` file is modified by this DRAFT.** On
coordinator APPROVAL, the core-agent implements both planes and runs the standing gate.

---

## 0. Design summary (one paragraph)

An `@overload` family is recognized at the `visit_FunctionDef` seam
(`Module5_IREmitter.py:3073`) by scanning `node.decorator_list` for a bare `Name("overload")` or
`Attribute(attr="overload")`. Each `@overload` stub is collected into a per-name pending list
(`self._pending_overloads[name]`) and is NOT emitted as a function IR node (its body is the
literal `...` / `pass` — R1, discarded at runtime; emitting a bodyless function would be dead
weight). For each stub, a **guarded postcondition** is synthesized: for each parameter with a
type annotation `T_i`, the guard is the existing `isinstance(p_i, T_i)` expression (the same
predicate vocabulary the Union/Optional narrowing seam and the body-level `isinstance` lowering
use — `_handle_isinstance` at `expressions.py:2024` emits `(subtag <typeof p_i> <T_i tag>)`, a
WhyML bool); the stub's `#@ ensures Q_i` (if any) is conjoined under the guard as
`isinstance(p_i, T_i) ==> Q_i` (the `==>` operator is parsed by `Module2_Parser` IMPL_OP at
`:1331` and lowered to WhyML `->` by `identifiers.py:23`; the existing `ensures { forall i. ...
-> ... }` pattern at `statements.py:171` confirms implication-in-ensures is supported). When the
final non-`@overload` implementation `def f(...)` is visited, the collected guarded
postconditions are appended to the implementation's `contracts.ensures` (after the user-written
ensures, like the Literal accumulator pattern at `:2763`). The implementation's single body must
prove each `G_i ==> Q_i` (O6) — Why3 discharges each as a separate VC under the guard
assumption. NO new IR node, NO IR_VERSION bump (reuses the existing `contracts.ensures` list +
the existing `==>`/`isinstance` lowering), NO `\trusted`. The runtime shim
(`src/pycsl_lib/typ/__init__.py:131`) already returns `func` unchanged; it is annotated with
`#@ ensures \result == val` (the identity postcondition, R1–R7) matching the cast/Union/Literal
shim convention. Byte-identical emission for every non-overload driver: the `@overload` detection
is a pure decorator-name test that fires only when `@overload` is present.

---

## 1. Normalization rule (front-end: `src/pycsl/frontend/`)

### 1.1 Surface forms to recognize

Per the two-plane spec §1.0 (O1, O1a, O1b):

| Surface | AST shape (post-`pure_ast`) | Disposition |
|---|---|---|
| `@overload def f(x: int) -> int: ...` | `FunctionDef(name="f", decorator_list=[Name("overload")], body=[Expr(Constant(Ellipsis))])` | collect into `_pending_overloads["f"]`; synthesize guard `isinstance(x, int) ==> <stub ensures>`; DO NOT emit a function IR node |
| `@overload def f(x: str) -> str: ...` | same shape, `int`→`str` | same — collect |
| `def f(x): <body>` (the implementation) | `FunctionDef(name="f", decorator_list=[], body=[...])` | emit normally; append the collected guarded postconditions to `contracts.ensures` |
| `@overload def f(x: int) -> int: return x` (non-`...` body) | `FunctionDef(..., body=[Return(...)])` | NOT an overload stub (O1a) — treat as a regular decorated function (byte-identical fallback) |

`overload` is recognized by the bare head name in `decorator_list` (the import-rewriting in
`import_classifier.py` already canonicalizes `from typing import overload`).

### 1.2 Canonical IR form

The implementation's IR is a standard function IR node with the guarded postconditions appended
to `contracts.ensures`. NO new top-level IR node, NO new field:

```
{ "name": "f",
  "contracts": {
    "requires": [...],            # unchanged
    "ensures": [
      ...user-written ensures..., # unchanged
      {"type": "BinOp", "op": "==>",
       "left":  {"type": "Call", "func": "isinstance",
                 "args": [{"type": "Var", "name": "x"}, {"type": "Var", "name": "int"}]},
       "right": <stub Q_i IR>},   # the guarded postcondition (O3)
      ...
    ],
    "assigns": [...], ...
  },
  "body": [...],                  # the single implementation body (O6 proves each guard)
  ...
}
```

The `==>` BinOp and the `isinstance` Call are EXISTING IR shapes (the same shapes the parser
produces for `#@ ensures isinstance(x, int) ==> (\\result == x)`). NO IR schema change, NO
IR_VERSION bump — the `contracts.ensures` list already holds arbitrary boolean IR expressions.

### 1.3 Normalization steps (in order)

1. **Pending-overload initialization** — in `PyCSLToJSONEmitter.__init__` (or at module-scope
   setup), add `self._pending_overloads: Dict[str, List[Dict[str, Any]]] = {}`. A per-name list
   of synthesized guarded-ensures IR clauses, awaiting the implementation.

2. **Stub recognition** — in `visit_FunctionDef` (`Module5_IREmitter.py:3073`), BEFORE
   `_build_function_ir`, check `_is_overload_stub(node)`: True iff (a) any `d` in
   `node.decorator_list` is `Name(id=="overload")` or `Attribute(attr=="overload")`, AND (b)
   `node.body` is exactly `[Expr(Constant(Ellipsis))]` or `[Pass]` (O1a — the `...`/`pass` body).
   If True:
   - call `_synthesize_overload_guard(node)` → returns a list of guarded-ensures IR clauses (one
     per stub `#@ ensures`, each wrapped as `isinstance(p_i, T_i) ==> Q_i`; if the stub has no
     `#@ ensures`, return `[]` — the guard is still synthesized for selection but contributes no
     VC, per O3);
   - append to `self._pending_overloads.setdefault(node.name, [])`;
   - RETURN without emitting a function IR node (the stub is discarded at runtime — R1; emitting
     a bodyless function would be dead weight and would collide with the implementation's name).
   *Byte-identical for non-overload drivers:* the check is a pure decorator-name + body-shape
   test; every non-`@overload` function skips it unchanged.

3. **Implementation attachment** — in `visit_FunctionDef`, for a NON-overload function whose
   name is in `self._pending_overloads`: after `_build_function_ir`, append
   `self._pending_overloads.pop(node.name)` to `func_ir["contracts"]["ensures"]`. Then proceed
   with the existing path (append to `program_ir["functions"]`, `generic_visit`).

4. **Guard synthesis** — `_synthesize_overload_guard(node)`:
   - For each `arg` in `node.args.args` (excluding `self`) that has an `annotation`:
     - resolve the type name `T_i` (a `Name` → `id`; an `Attribute` → `attr`; lowercased for
       the existing `int`/`str`/`bool`/`bytes`/`float` vocabulary);
     - build the guard IR `{"type": "Call", "func": "isinstance",
       "args": [{"type": "Var", "name": arg.arg}, {"type": "Var", "name": T_i}]}`.
   - The combined guard for the stub is the conjunction of per-parameter guards (a single
     parameter ⇒ the guard itself; multiple ⇒ nested `and` BinOps). For the monomorphic TY2
     scope each stub has exactly one typed parameter, so the guard is the single isinstance call.
   - For each `#@ ensures Q_i` clause on the stub (from `getattr(node, 'csl_ensures', [])`):
     wrap as `{"type": "BinOp", "op": "==>", "left": <guard>, "right": <Q_i IR>}` and append.
   - Return the list. A stub with no `#@ ensures` returns `[]` (O3 — no VC, guard still
     synthesized for selection at call sites via the argument-type assignability check, which is
     native Why3 type-checking when the implementation's parameter is typed).

### 1.4 Front-end files that change (on APPROVAL)

| File | Change |
|---|---|
| `src/pycsl/frontend/Module5_IREmitter.py` | add `_pending_overloads` init, `_is_overload_stub`, `_synthesize_overload_guard`, `_build_overload_param_guard`, `_overload_type_name`; dispatch from `visit_FunctionDef` (`:3073`). The existing `_build_function_ir` is NOT modified (byte-identical for non-overload). |

### 1.5 CSL contract placement (stub `#@ ensures`)

A stub's `#@ ensures Q_i` must precede the `@overload` decorator (the standard CSL
contract-placement convention — Module1's harvester associates a `#@` comment with the
*next* statement's `def` line, and a `#@` between `@overload` and `def` lands on the
decorator line, not the `def` line). The canonical stub form is:

```python
#@ ensures \result == x      # the stub's postcondition (PRECEDES @overload)
@overload
def f(x: int) -> int: ...
```

### 1.6 Implementation parameter annotation (TY2 scope restriction)

For the guard `isinstance(p_i, T_i)` to be a **decided** type judgment (not a symbolic
`typeof_op` placeholder), the implementation's parameter must carry a type annotation that
the symbol table resolves. PEP 484 does not require the implementation to be annotated (only
the stubs carry types), but for the TY2 monomorphic scope PyCSL requires the implementation
to be annotated so the guard decides (O4 — the argument's static type selects the active
overload by type-based assignability, decided by Why3/SMT from the parameter's static type).
This is a legitimate divergence-by-strictness (§0: the static lower bound may be stricter
than S1). An unannotated implementation yields a symbolic guard (sound but imprecise — the
call-site selection VC is discharged only when the body unconditionally establishes the
postcondition). The conformance subset (§5) uses annotated implementations.

---

## 2. Lowering table entry (Module 6: `src/pycsl/module6_whyml/`)

### 2.1 The lowering

The guarded postcondition `isinstance(p_i, T_i) ==> Q_i` lowers through the EXISTING
`_emit_contracts` path (`functions.py:266`): each `ensures` clause is rendered via
`_expr_to_whyml`, which handles `BinOp("==>")` via the existing identifier map
(`identifiers.py:23` maps `==>` → `->`) and `Call("isinstance", ...)` via `_handle_isinstance`
(`expressions.py:2024` → `(subtag <typeof p_i> <T_i tag>)`). The resulting WhyML line is
`ensures { (subtag (typeof x) <int_tag>) -> <Q_i whyml> }`. NO new Module 6 code.

### 2.2 Per-clause VC mapping (the load-bearing part)

| Clause | Static obligation | VC / mechanism |
|---|---|---|
| **O2** (guard per stub) | each stub's parameter type `T_i` yields a guard | The guard is the `isinstance(p_i, T_i)` IR, emitted as `(subtag (typeof p_i) <T_i tag>)` — a WhyML bool. NO separate VC; the guard is the antecedent of O3. |
| **O3** (guarded postcondition) | `ensures { G_i -> Q_i(\result) }` per stub | One `ensures` clause per stub carrying a `#@ ensures`. Why3 emits one VC per clause: under assumption `G_i`, prove `Q_i`. |
| **O4** (selection at call sites) | at `f(v)`, the argument type selects the active overload | Native Why3 type-checking: the implementation's parameter is typed; the call's argument must be assignable. The guarded postconditions are ALL available at the call site (Why3 exposes every `ensures` of the callee); the caller proves the specific `G_i -> Q_i` it needs by establishing `G_i` (the argument's type predicate). NO new call-site VC — the existing call-VC machinery picks up the extra `ensures`. |
| **O5** (selection is type-based, NOT runtime-dispatch-based) | the static selection VC must NOT be discharged by runtime isinstance | The guard `G_i` is a WhyML formula over the parameter's TYPE TAG (`subtag (typeof x) ...`), decided by Why3/SMT from the static type — NOT by executing the implementation's `isinstance` branch. The implementation's runtime `isinstance` is body code (a value check); the guard is a spec formula (a type judgment). They are different WhyML terms. NO-BLEND by construction. |
| **O6** (implementation proves each guarded postcondition) | the single body proves each `G_i -> Q_i` | One Why3 VC per guarded postcondition: assume `G_i` (the parameter's type predicate holds), prove `Q_i` from the body. The body's runtime `isinstance` branches are visible to Why3 as facts, so under `G_i` the matching branch's postcondition is provable. This is the "guarded contract family proved against the single implementation" (TY2 hard rule). |

### 2.3 The lowering seam (concrete file changes)

| File | Change |
|---|---|
| `src/pycsl/module6_whyml/functions.py` | **No change.** The existing `_emit_contracts` (`:266`) renders the appended `ensures` clauses (including `==>` and `isinstance`) via the existing expression lowering. |
| `src/pycsl/module6_whyml/expressions.py` | **No change.** `_handle_isinstance` (`:2024`) and the `==>` identifier map (`identifiers.py:23`) already lower the guard. |
| `src/pycsl/core_ir_semantic.py` | **No change.** The guarded postconditions are standard `ensures` clauses; no new semantic check is required. (O1b's "exactly one implementation" is enforced structurally: if no implementation follows the stubs, the pending list is silently dropped — a future enhancement could raise; for TY2 the conformance subset covers it.) |

---

## 3. Shim contract (runtime plane: `src/pycsl_lib/typ/__init__.py`)

Per the two-plane spec §2 (R1–R7) and the no-blend rule (D4), the runtime shim exposes the
`overload` decorator as an identity that performs **NO validation**. The current
`src/pycsl_lib/typ/__init__.py:131` already has `def overload(func): return func`; it is
annotated with the identity postcondition matching the cast/Union/Literal/TypedDict/NamedTuple
convention.

### 3.1 Shim surface

```python
# In src/pycsl_lib/typ/__init__.py — overload decorator, Shimmed (R1–R7).

#@ ensures \result == val
def overload(func, val) -> int:
    return val
```

(The `-> int` return tag and `val` parameter are the existing PyCSL convention for opaque
runtime objects — the same convention `cast`/`Union`/`Literal`/`Final`/`TypedDict`/`NamedTuple`
use. The WhyML model is `int`-typed and the runtime object is opaque to the verifier; this is
the established Modelled-for-identity pattern. The `val` parameter carries the identity
postcondition. The real runtime `overload(func)` registers `func` and returns `_overload_dummy`
(S4); the shim models this as identity — the stub is discarded at runtime (R1) and the
implementation runs (R2); the shim performs no type enforcement (R3/R6).)

### 3.2 Contract discharges each R-clause

| R-clause | How the shim honours it |
|---|---|
| R1 (stub bodies discarded) | The shim does not execute stub bodies — `@overload` stubs have `...` bodies (O1a) and are not emitted as functions (§1.3). The shim's identity models the decorator returning a dummy. |
| R2 (the implementation runs) | The implementation is a plain function emitted normally; the shim does not intercept it. |
| R3 (no type enforcement at runtime) | The shim's `#@ ensures \result == val` carries ONLY the identity postcondition. There is no `requires` on the argument types. |
| R4 (isinstance dispatch is implementation logic) | The shim does NOT model the implementation's isinstance branches — those are body code, lowered through the existing statement path. The static guard (O2/O5) is a spec formula, not the runtime isinstance. |
| R5 (get_overloads introspection) | `get_overloads` is not in the verified surface for TY2 (it returns a list of function objects — opaque to the verifier). A future enhancement may shim it as `ensures \result >= 0`. |
| R6 (no validation in the shim) | The shim performs NO check on whether a call matches an overload's parameter types. A shim that DID check would be unfaithful in exactly the way an over-strong axiom is (D4). |
| R7 (the implementation is a plain function) | The runtime plane of the implementation is the plain-function plane; the shim's only job is the decorator object. |

### 3.3 Why the runtime shim does NOT discharge any static clause

This is the no-blend rule (D4) made concrete: the shim's `ensures \result == val` is
SATISFIED by every value regardless of type. The static clauses O2–O6 are discharged by Why3
type-checking + SMT over the guarded postconditions (§2.2), which is invisible to the shim. A
conformance-agent authoring the S5 subset from the two-plane spec + the shim surface alone
cannot reverse-engineer the lowering — the independence-based Gate C (c) holds.

---

## 4. Classification (`--soundness-report`)

Per the two-plane spec §4, the classification is **dual** (both planes, separately):

| Plane | Classification | Tag |
|---|---|---|
| Static | **Interpreted** | the `@overload` family is consumed by the static plane and lowered to a guarded contract family attached to the implementation (per §2.2) |
| Runtime | **Shimmed** | the runtime meaning is the discard-and-plain-function behaviour + the introspectable registry, no enforcement (per §3) |

### 4.1 GT gap codes tagged for `@overload`

- **GT7** (analogous, NOT a new code) — D1 documents the `isinstance`-dispatch no-blend trap:
  the static O4/O5 type-based-selection obligation must NOT be discharged by any runtime
  `isinstance` check in the implementation (R4 is value dispatch, not type judgment). Tagged
  in the report as a `no_blend_overload_isinstance` note.
- **GT8** — the S5 conformance subset for `@overload` is the conformance-agent's standing
  artifact (NOT this DRAFT's deliverable). Each clause O2–O6 above names the S5 case shape
  it commits to.

No other GT gap is tagged for `@overload` at TY2.

---

## 5. Standing gate plan (total additivity)

Per `typing-global-impl.md` §4 Gate B and the core-agent's hard rules:

### 5.1 Byte-identical emission for unaffected drivers

- The `_is_overload_stub` check is a pure decorator-name + body-shape test: for any function
  that does NOT carry `@overload`, `visit_FunctionDef` proceeds exactly as before. Every
  non-overload driver produces byte-identical IR and byte-identical WhyML.
- The `_pending_overloads` dict is empty for every module that has no `@overload` stubs; the
  implementation-attachment step is a no-op (the `name in self._pending_overloads` test is
  False).
- The corpus byte-diff gate (`bin/byte-diff-sweep.sh` / the standing gate) MUST remain
  green for every non-overload driver. A byte-diff on an unaffected driver is a regression.

### 5.2 `os` proof + `formal_<name>` suite re-confirmed

- The `os` library (now fully green) does NOT use `@overload` in its verified surface —
  confirm by `rg '@overload|overload' src/pycsl_lib/os/` before claiming additivity. (Expected:
  zero matches in verified code; any match is a comment-only reference.)
- The `formal_<name>` suite (json, re, warnings, …) is re-run; every previously-green
  formal test MUST remain green.

### 5.3 IR-conformance corpora

- **No IR_VERSION bump.** The `@overload` construct reuses the EXISTING `contracts.ensures`
  list and the EXISTING `==>` / `isinstance` IR shapes. NO new IR node, NO new field. The IR
  schema is unchanged; `IR_VERSION` stays at its current value; `ACCEPTED_IR_VERSIONS` is
  unchanged. The IR-conformance corpora (core + front-end `*.ir.json` / `*.expected.mlw`) MUST
  remain green unchanged for every non-overload driver.

### 5.4 doc-coherency green

- `test-suite/annotations.md`: add the canonical entry for the `@overload` annotation
  surface (citing S2 PEP 484). Per `pycsl-doc-coherency` skill, the entry must also appear in
  `docs/pycsl-concrete-syntax-reference.md`, `docs/pycsl-static-semantics-reference.md`,
  `docs/pycsl-translational-reference.md`, and a `config/skills/` skill (`pycsl-annotate`).
  `bin/doc-coherency.py --check` MUST remain green.

### 5.5 Non-vacuity gate

- The overload VCs (O3/O6 — each `G_i -> Q_i` guarded postcondition) are real `ensures` VCs.
  `--check-vacuity` MUST be green on each. A false-twin (an impossible `Q_i` under `G_i`)
  MUST FAIL — confirming the guarded postcondition is non-vacuous. The guard `G_i` is
  satisfiable (a value of type `T_i` exists), so the context is consistent; the vacuity gate
  does not flag a faithful guarded postcondition.

---

## 6. NoReturn × vacuity gate

**N/A for `@overload`.** The NoReturn × vacuity interaction is owned by the `NoReturn`
construct's spec. `@overload` does not interact with the vacuity gate in the NoReturn-specific
way. (A stub annotated `-> NoReturn` would contribute `G_i -> false`, which is a legitimate
guarded-postcondition VC, not a vacuity signal — but the TY2 conformance subset does not
exercise this combination.)

---

## 7. Deliverable checklist (on APPROVAL)

- [ ] Front-end: `_pending_overloads` init, `_is_overload_stub`, `_synthesize_overload_guard`
      in `Module5_IREmitter.py`; dispatch from `visit_FunctionDef`.
- [ ] Module 6: NO change (reuses existing `ensures` / `==>` / `isinstance` lowering).
- [ ] `core_ir_semantic.py`: NO change.
- [ ] `src/pycsl_lib/typ/__init__.py`: `overload` shim annotated with identity
      `ensures \result == val`.
- [ ] `test-suite/annotations.md` (§12.14) + three reference docs;
      doc-coherency green.
- [ ] `--soundness-report`: `overload` classified Interpreted (static) /
      Shimmed (runtime), GT7-analog note documented.
- [ ] Standing gate: corpus byte-diff green for non-overload drivers;
      `os` proof SUCCESS; formal suite SUCCESS; NO IR_VERSION bump;
      `--check-vacuity` green on the new overload VCs.
- [ ] NO conformance-suite or shim-faithfulness-driver edits beyond the
      conformance-agent's own artifacts.
