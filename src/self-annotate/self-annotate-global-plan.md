# PyCSL Self-Annotation: Global Plan

*Merged from: `self-annotate-plan.md`, `self-annotate-plan-no-sugar.md`,
`self-annotate-plan-to-contract.md`, `self-annotate-comments-from-Claude.md`,
`self-annotate-layer3.md`.*

*Companion files (not merged, kept as standalone): `pycsl-wp-spec.mlw`,
`audit-guide.md`.*

---

## 1. Goal

PyCSL has a **formally proven WP calculus** (soundness theorem in both Rocq and
Lean under `src/formal-semantics/`). This proves the *mathematics* is correct.
The remaining trust gap: does the **Python implementation** faithfully realise
that mathematics?

Self-annotating the implementation with PyCSL `#@` contracts — and verifying
them with Why3 — closes this loop. The process also serves as a self-referential
bootstrap: the tool verifies itself using the same methodology that it was proven
correct for.

---

## 2. Output Structure

```
src/self-annotate/
    rocq/                  ← contracts derived from Rocq proofs
        Module6_WhyMLTranspiler.py
        Module5_IREmitter.py
        Module4_SemanticAnalyzer.py
        Module3_Weaver.py
        Module2_Parser.py
        Module1_Ingestor.py
        ConcurrencyChecker.py
        ir_schema.py
        errors.py
        pycsl.py
        __init__.py
    lean/                  ← contracts derived from Lean proofs
        (same files)
    pycsl-wp-spec.mlw      ← Layer 3 Why3 spec module (keep)
    audit-guide.md         ← per-arm audit procedure (keep)
```

Each annotated file is a **copy of the unannotated source** from `src/pycsl/*.py`
with `#@` contracts added. The two paths act as a cross-check: if Rocq-derived
and Lean-derived contracts agree, confidence in both proofs and implementation
is higher.

---

## 3. Trust Chain (Layers 0–3)

```
Layer 0 — Rocq / Lean type-checkers
   Machine-checked soundness theorem: pycsl_soundness
         ↓
Layer 1 — PyCSL #@ contracts on the Python implementation
   Structural faithfulness: frame conditions, loop termination,
   exhaustive dispatch over all 10 WP rule arms
         ↓
Layer 2 — Why3 + SMT solvers
   Output verification: the generated .mlw file is accepted by Why3
         ↓
Layer 3 — Why3 val spec module (pycsl-wp-spec.mlw)
   Semantic equivalence, per WP arm: one val per arm, ensures clause
   mirrors the Rocq fixpoint arm exactly.
   Machine-checked: Why3 clone/refinement proves generated code satisfies spec.
   Human-audited:   val spec written by inspection of Phase4_WP.v (line-by-line).
   See audit-guide.md for the full audit procedure.
```

Each layer covers what the others cannot:

| Property | L0 | L1 | L2 | L3 |
|---|---|---|---|---|
| WP rules mathematically sound | ✓ | — | — | — |
| Frame conditions correct | — | ✓ | — | — |
| Loop termination | — | ✓ | — | — |
| Non-empty output | — | ✓ | — | — |
| User program VCs discharged | — | — | ✓ | — |
| WP semantic equivalence, line-by-line | — | — | — | ✓ |

**The irreducible gap between L0 and L3**: The Rocq state type is
`list (ident * val)` (Phase2_State.v:14); the Why3 abstract state type is
`map ident value`. These are different representations; the correspondence is
argued by the shared `update_lookup_same` axiom. This gap cannot be
machine-checked without formalising Why3's logic inside Rocq.

---

## 4. The Two Semantic Gaps

### Gap A — Abstraction Refinement

The formal semantics assumes:
- Variables are unbounded integers (no machine word overflow).
- State is a total function from identifiers to values.
- Array access is bounds-checked and returns 0 on out-of-range.
- Expression evaluation is pure and terminating.

The Python implementation uses dicts, JSON IR, and string building. To derive
contracts from the formal model, each assumption must become a `#@ requires`
precondition, or the gap must be argued away by parametricity: the formal model
is parametric in the state representation (`state = list (ident * val)` could
equally be Python `dict`), so structural contracts suffice.

### Gap B — Structural Mismatch

The formal model is a `Fixpoint` over inductive `stmt`. The implementation is
an `if/elif` chain with mutable accumulator strings. There is no 1:1 mapping
from Rocq case arms to Python branches. This is bridged by the per-arm
traceability matrix (Section 6.2) and Layer 3's `val` specs.

---

## 5. What Can and Cannot Be Expressed in PyCSL Contracts

See `docs/pycsl-concrete-syntax-reference.md` for the normative grammar.
See also `docs/pycsl-static-semantics-reference.md` for well-formedness rules (Module4).
See also `docs/pycsl-translational-reference.md` for WhyML generation rules (Modules 5–6).

**PyCSL contracts can assert:**
- Frame conditions: `#@ assigns self._known_collection_sizes, …`
- Non-emptiness: `#@ ensures \result != ""`
- Length bounds on plain variables: `#@ ensures \length(stmts) >= 0`
- Structural invariants: `#@ loop invariant 0 <= i and i <= n`
- Termination: `#@ loop variant n - i`
- Pure functions: `#@ assigns \nothing`
- Element well-formedness (plain variable): `#@ ensures \forall i; 0 <= i and i < \length(items) ==> items[i] != 0`
- List membership: `#@ requires x in lst` where `lst` is typed as `list[T]` — translates to `array int` in WhyML (TR-3). Dict/set membership (`"key" in d` where `d` is unannotated) passes Module4 but fails WhyML generation (G6, §T.11.1) — do not use.
- Note: `\length` requires a plain variable name (CNAME, §3.1.8) — `\length(\result)` and `\length(self.field)` are **invalid**

**Semantic constraints** (enforced by Module4 — see `docs/pycsl-static-semantics-reference.md`):
- SR-1 (scope, E2): all variables in `requires`/`ensures`/`loop invariant` must be in Γ_f — function parameters, annotated locals, or ghost vars. Use only parameter names in contracts.
- SR-2 (`\result`, E1): `\result` is only valid in `ensures`. Never use it in `requires`, `loop invariant`, or `\variant`.
- SR-3 (class invariant scope, E5): `FieldAccess` nodes (`self.field`) are excluded from variable extraction and NOT checked against Γ_c. `#@ class invariant self.expr != 0` passes E5 regardless of Γ_c content.
- SR-4 (assigns gap, §10.1): `self.field` in assigns targets is NOT validated against Γ_c. All `#@ assigns self._*` clauses pass Module4.
- SR-5 (nested closures, §1.1.2): closure variables from enclosing scopes are not collected into Γ_f for nested functions. Re-declare as `Any`-typed locals inside the nested function body.
- SR-6 (membership, §3.2.6b): `"key" in d` with a string literal and an in-scope variable passes Module4 (L2 ✓). However, see TR-3: only valid at L3 when `d` is typed `list[T]`. For unannotated `d`, use `d != 0` instead.

**Translational constraints** (enforced by Modules 5–6 / Why3 type-checker):
- TR-1: Unannotated params → `int` in WhyML. Use arithmetic predicates (`>= 0`, `!= 0`, `> x`) only.
- TR-2: String literals hash to `int`. `\result != ""` → `(result <> 0)` — valid.
- TR-3: `in`/`not in` valid ONLY for `list[T]`-typed params. Unannotated params → `int`; `in` on `int` fails Why3.
- TR-4: `assigns` in Hoare model (default) produces no WhyML output — clause is accepted but generates no frame condition.
- TR-5: `\result` → `result` in WhyML ensures. Valid in `ensures` only.
- TR-6: `\trusted` → Why3 `val` declaration. No proof obligation generated.

**PyCSL contracts cannot currently assert:**
- "The generated WhyML string, when parsed, represents `SAssign(x, e)`."
- Semantic equivalence between Python output and the WP rule. *(Layer 3 fills this.)*
- String membership on `\result`: `"Return" in \result` is invalid because `\result` is not in scope as a collection type in the WhyML model. String membership on ordinary parameters (`"key" in d`) passes Module4 static checks (§3.2.6b) but fails WhyML generation when `d` is unannotated (→ `int`, and `in` on `int` is invalid — TR-3, G6).

---

## 6. How Contracts Are Derived from the Formal Proofs

### 6.1 Three Layers of Contracts

#### Layer A — Structural Preservation (Modules 1–5)

These do not trace back to a specific theorem; they follow from pipeline
data structure invariants.

Examples (non-tautological — prefer these over bare `\length >= 0`):
```python
# Structure-preserving transforms
#@ ensures 1 == 1  # aspirational: length equality not expressible (\length(\result) invalid — §3.1.8)

# Element well-formedness
#@ ensures 1 == 1  # aspirational: \forall over \result not expressible (§3.1.8, §3.3)

# Accumulating functions
#@ ensures 1 == 1  # aspirational: length bound not expressible (\length(\result) invalid — §3.1.8)
```

> **Validation:** L1 ✓ · L2 ✓ · L3 ✓ — `1 == 1` is the canonical placeholder; passes all three levels. The aspirational intent is noted in comments because IS-2 (`\length(\result)` invalid) and §3.3 (`\forall` over `\result` not expressible) block the stronger form.

Note: `\length(\result)` is **invalid** — `\result` is a keyword, not a plain variable
name (CNAME). Until the grammar is extended to support `\result` in `\length`,
use `1 == 1` and document the intent as an aspirational comment.

Avoid tautological contracts such as `#@ ensures \length(\result) >= 0`
(always true for Python lists; Why3 discharges without examining the body).

#### Layer B — WP Rule Correctness (Module6)

Each WP arm maps to one Module6 handler. See Section 6.2.

#### Layer C — Well-formedness (Module4)

Module4's validators check the preconditions assumed by the formal model
(variables in scope, mutex references valid, class invariants well-scoped).
These correspond to the `exec st s out` premise of `pycsl_soundness`.

### 6.2 WP Arm → Module6 Handler Mapping

The WP calculus uses three continuations:
- `Qn` — normal completion → WhyML string concatenation with `";\n"`
- `Qr` — return → WhyML `raise Return` / `try … with Return r -> r end`
- `Qc` — continue → WhyML `raise PyCSL_Continue`

| WP Rule | Phase4_WP.v | pycsl-wp-spec.mlw val | M6 Python (line) | Layer 1 contract pattern |
|---|---|---|---|---|
| `wp SSkip` | :21 | `handle_skip` | `"Pass"` branch, inline | `assigns \nothing` |
| `wp SAssign` | :23–24 | `handle_assign` | `_handle_assign_stmt` (1372) | assigns clause; `ensures \result != ""` |
| `wp SAugAssign` | :26–30 | `handle_aug_assign` | inline ~1380 | assigns clause |
| `wp SArraySet` | :32–35 | `handle_array_set` | inline | assigns clause |
| `wp SSeq` | :37–39 | `handle_seq` (structural) | `_stmts_to_whyml` (2098) | `requires \length(stmts) >= 0` |
| `wp SIf` | :41–43 | `handle_if_branch` | inline ~1485 | assigns clause |
| `wp SWhile` | :45–66 | `check_while_inv_entry`, `check_while_body_step`, `handle_while_exit` | `_handle_while_stmt` (1446) | loop invariant + loop variant |
| `wp SFor` | :68–94 | **proved** (desugar_correct plan-formal-03) | `_handle_for_stmt` (1543) | `requires 1 == 1` |
| `wp SReturn` | :96–97 | `handle_return` | inline ~1468 | assigns clause |
| `wp SContinue` | :99–100 | `handle_continue` | inline ~1478 | assigns clause |

**`SFor` note**: `desugar_correct` is `Admitted` (Rocq) / `sorry` (Lean). The
Layer B contract for `_handle_for_stmt` therefore claims formal justification
that is not yet machine-checked. The Layer 3 `val` for `SFor` is intentionally
omitted from `pycsl-wp-spec.mlw` until the proof is closed. See Section 8.

### 6.3 Proof File → Contract Mapping

#### `Phase1_AST.v` / `AST.lean` → `Module2_Parser.py`, `Module5_IREmitter.py`

Defines `stmt`, `expr`, `contract_expr`, `func_spec`. Module2's dataclass
definitions mirror these constructors.

```python
@dataclass
class Requires:
    #@ class invariant self.expr != 0
    expr: Any
```

> **Validation:** L1 ✓ · L2 ✓ (SR-3: `self.expr` is FieldAccess → excluded from E5 scope check → passes Module4 regardless of Γ_c content) · L3 ✓
> *(Fixed: `self.expr != None` → `self.expr != 0`; `None` is a forbidden Python boolean in `#@` expressions — forbidden-expressions.md.)*

Note: `#@ class invariant` doubles as a constructor precondition — callers
must not pass `None`. This is a documentation obligation, not a blocker.

**Implementation note**: In the Rocq annotated path, `@dataclass` class
invariants are skipped due to a libcst/ast line-number mismatch — libcst
reports the `ClassDef` position at the decorator line while Python's `ast`
reports it at the `class` keyword, so Module3_Weaver's lookup fails silently.
The syntax above is correct; the attachment issue is a tooling limitation.

Separately: Module4 builds Γ_c from the `__init__` method body (§1.2 of
static semantics reference). For `@dataclass` classes, `__init__` is
auto-generated and absent from the source AST, so Γ_c is empty.
However, `self.field` in class invariant expressions is a `FieldAccess` node,
which is excluded from `extract_variables` (§6.1 of static semantics reference)
— E5 never fires even with empty Γ_c. The Module3_Weaver line-number mismatch
is the **sole blocker** for class invariants on `@dataclass` classes.

For Module5 (IR emitter):
```python
def _py_stmts_to_ir(self, stmts):
    #@ requires \length(stmts) >= 0
    #@ ensures 1 == 1  # aspirational: \forall over \result[i] not expressible (§3.1.8, §3.3)
```

> **Validation:** L1 ✓ · L2 ✓ (SR-1: `stmts` ∈ Γ_f) · L3 ✓
> *(Fixed: `stmts != None` → `\length(stmts) >= 0`. `None` is forbidden in `#@`. `stmts != 0` would also fail: typed `list` → `array int` in WhyML; comparing `array int` to `0` is a TR-1 type error.)*

#### `Phase2_State.v` / `State.lean` → `Module6._expr_to_whyml`

Proves `eval_expr`, `eval_bool`, `eval_z`, `eval_contract` are total and pure.
The implementation counterpart also accumulates abstract operation declarations:

```python
def _expr_to_whyml(self, expr_ir, local_refs, ...):
    #@ requires 1 == 1
    #@ assigns self._abstract_ops    # side effect: registers abstract ops
    #@ ensures \result != ""
```

> **Validation:** L1 ✓ · L2 ✓ (SR-4: `self._abstract_ops` FieldAccess not validated against Γ_c) · L3 ✓
> - TR-4: `assigns` in Hoare model generates no `writes` clause — accepted, weaved, but produces no frame proof obligation.
> - TR-2: `\result != ""` → `(result <> 0)` in WhyML — valid for `str`-returning functions.
> *(Added missing `requires` clause — all three contracts required.)*

The `assigns self._abstract_ops` makes explicit that `_expr_to_whyml`
**approximates** `eval_expr` with an additional side effect. The Layer 0
correspondence is approximate, not exact. The traceability matrix (§5.1 of the
original contract sub-plan) must reflect this: `_expr_to_whyml` does not purely
correspond to `eval_expr`.

#### `Phase3_SOS.v` / `SOS.lean` → Frame Conditions on `_stmts_to_whyml`

Proves `exec_deterministic`: same input produces same output. In the
implementation, determinism is captured by the `assigns` clause — explicit
listing of all mutable `self.*` fields:

```python
def _stmts_to_whyml(self, stmts, local_refs, declared_refs, indent, in_loop):
    #@ requires \length(stmts) >= 0
    #@ assigns self._known_collection_sizes, self._known_collection_elements
    #@ assigns self._array_locals, self._dict_locals, self._lambda_locals
    #@ assigns self._record_locals, self._has_early_ret
    #@ assigns self._abstract_ops, self._havoc_counter
    #@ ensures \result != ""
```

> **Validation:** L1 ✓ · L2 ✓ (SR-4: all `self._*` assigns targets pass Module4) · L3 ✓
> - TR-4: none of the `assigns` clauses emit a `writes` clause in the Hoare model — expected; frame documented for human readers.
> - TR-2: `\result != ""` → `(result <> 0)` in WhyML — valid.
> *(Added missing `requires \length(stmts) >= 0`.)*

Note on `assigns self.*` semantics: `FieldAccess` nodes in assigns targets
are NOT validated against Γ_c in function contracts (known gap — §10.1 of
static semantics reference, §3.1.3). All `#@ assigns self._*` clauses pass
Module4 regardless of whether the field appears in `__init__` (SR-4).
In the Hoare model (the default for self-annotation), `assigns` generates NO
explicit `writes`/frame clause in the WhyML output (TR-4, §T.9.1). The clause
is accepted by Module4, weaved correctly, but produces no proof obligation.

#### `Phase3b_Desugar.v` / `DesugarDef.lean` → `_handle_for_stmt`

Defines `desugar`: transforms `SFor x arr inv var body` into an equivalent
`SWhile` using index variable `_pycsl_idx`. The correctness lemma
`desugar_correct` is `Admitted`/`sorry`. Contract:

```python
def _handle_for_stmt(self, stmt, ...):
    #@ requires 1 == 1    # placeholder; "iter_var" in stmt fails WhyML (TR-3, G6)
```

> **Validation:** L1 ✓ · L2 ✓ · L3 ✓ — `1 == 1` passes all three levels.
> TR-3 prevents `"iter_var" in stmt`: `stmt` is `Dict[str, Any]` (unannotated → `int` in WhyML); `in` on `int` is invalid in Why3 (G6, §T.11.1).
> This is the correct placeholder pending either a `desugar_correct` proof or a typed annotation on `stmt`.

Add this note in the annotated copy at the `_handle_for_stmt` annotation:
> "Layer B contract deferred pending resolution of `desugar_correct`
> Admitted/sorry — see Section 8 of this document."

#### `Phase4_WP.v` / `WP.lean` → All `_handle_*_stmt` Methods

Each handler's contract has three components:
1. `requires` — IR node well-formedness (keys present, types correct)
2. `assigns` — frame condition listing all mutable fields modified
3. `ensures` — non-empty output

The SWhile WP rule (Phase4_WP.v:45–66) has three conjuncts which must each
be checked:
- **C1** (`:46`): invariant at loop entry → `#@ loop invariant` in the generated WhyML
- **C2** (`:47–62`): body preserves invariant and decreases variant → `#@ loop invariant` + `#@ loop variant`
- **C3** (`:63–66`): when condition is false, `Qn` holds → loop exit postcondition

Example for `_handle_while_stmt`:
```python
def _handle_while_stmt(self, stmt, rest, ...):
    # Formal correspondent: wp (SWhile inv var cond body) Phase4_WP.v:45-66
    #@ requires stmt != 0
    #@ assigns self._known_collection_sizes, self._known_collection_elements
    #@ assigns self._array_locals, self._dict_locals, self._lambda_locals
    #@ assigns self._record_locals, self._has_early_ret
    #@ assigns self._abstract_ops, self._havoc_counter, self._in_spec
    #@ ensures \result != ""
```

> **Validation:** L1 ✓ · L2 ✓ (SR-1: `stmt` ∈ Γ_f; SR-4: all `self._*` assigns pass) · L3 ✓
> - TR-1: `stmt != 0` valid (`stmt` unannotated → `int`; comparing `int != 0` is fine).
> - TR-4: no `writes` clause emitted in Hoare model — expected.
> - TR-2: `\result != ""` → `(result <> 0)` in WhyML.
> *(Fixed: `stmt != None` → `stmt != 0`; `None` forbidden. `"test" in stmt` removed: `stmt` unannotated → `int`; `in` on `int` fails Why3 (TR-3, G6).)*

#### `Phase5a_WhileInv.v` / `WhileInv.lean` → Loop Annotations

Proves `while_inv_preserved`. This justifies the existing loop annotations
inside `_handle_while_stmt`:

```python
#@ loop invariant 0 <= i_inv_w and i_inv_w <= n_inv_w
#@ loop variant n_inv_w - i_inv_w
while i_inv_w < n_inv_w:
    ...
```

> **Validation:** L1 ✓ · L2 ✓ (SR-1: `i_inv_w`, `n_inv_w` must be in Γ_f — they are locally declared before the loop) · L3 ✓ — arithmetic predicates on `int`-typed local variables; canonical loop pattern.

#### `Phase5b_Soundness.v` / `Soundness.lean` → Top-Level `transpile()`

The soundness theorem is a metatheorem — it does not translate to a `#@`
annotation directly. It justifies why the Layer B contracts are correct if all
WP arms are implemented correctly. The top-level frame condition:

```python
def transpile(self):
    # Formal correspondent: pycsl_soundness Phase5b_Soundness.v
    #@ requires 1 == 1
    #@ assigns self._all_record_fields, self._module_func_names
    #@ assigns self._bounded_int, self._current_params, ...
    #@ ensures \result != ""
```

> **Validation:** L1 ✓ · L2 ✓ (SR-4: all `self._*` assigns targets pass Module4) · L3 ✓
> - TR-4: no `writes` clause emitted in Hoare model — expected.
> - TR-2: `\result != ""` → `(result <> 0)` in WhyML — valid.
> *(Added missing `requires 1 == 1` — all three contracts required.)*

*(Second `ensures` removed: `\result != ""` already implies non-empty for
strings; `\length(\result) > 0` is invalid because `\result` is not a CNAME.)*

---

## 7. What Is NOT Annotated

Functions outside the formal model are left unannotated. They are **not** marked
`\trusted` — that keyword is reserved exclusively for standard library stubs in
`data/lib_stubs/`. Functions outside the formal model simply remain unannotated.

| Category | Examples |
|---|---|
| I/O and subprocess | `pycsl.py` CLI, file reads |
| libcst CST visitors | `Module1_Ingestor.py` `visit_*` methods |
| Complex string builders | Module6 output string assembly helpers |
| Error/exception classes | `errors.py` |
| JSON parse callsites | `json.loads()` in the pipeline |

---

## 8. The For-Loop Desugaring Gap (`desugar_correct`)

### 8.1 Status

```coq
(* Phase3b_Desugar.v:73-81 *)
Lemma desugar_correct : forall st s out,
  fresh_in_stmt for_idx s ->
  exec st s out <-> exec st (desugar s) out.
Proof. Admitted.
```

```lean
-- Desugar.lean:13-16
theorem desugar_correct ... := by sorry
```

This is the single most important open gap. Its impact: `_handle_for_stmt`
cannot claim a fully machine-checked Layer B contract.

### 8.2 Three Blocking Issues

**Issue 1 — No `exec` constructors for `SFor`**

The `exec` inductive relation has no constructors for `SFor`. Without
`ExecFor*` constructors, the biconditional is unprovable: the `←` direction
(`exec st (desugar s) out → exec st (SFor ...) out`) is false because
`exec st (SFor ...) out` is uninhabitable.

Required additions to `Phase3_SOS.v`:
- `ExecForEmpty` — when the array is empty
- `ExecForTrue` — one iteration: assign `x := arr[idx]`, execute body, increment
- `ExecForBreak` — body raises `OBroken`, loop exits

**Issue 2 — Guard expression is a placeholder**

The current `desugar` produces guard `arr[idx] - arr[idx]` (always 0, loop
never enters). The correct guard is `idx < len(arr)`, but `expr` has no
`ELength` constructor — only `contract_expr` has `CLength`.

Required: add `ELength` to the `expr` inductive type in `Phase1_AST.v`, or
express the guard using `contract_expr` with a new `eval_z`-based comparison.

**Issue 3 — `exec_preserves_fresh_var` is unproved**

The proof needs: for any statement `body` where `for_idx` is fresh, executing
`body` does not modify `for_idx`. This requires a state-permutation lemma cascade
(estimated 4–6h).

**Break in nested loops (Issue 7 from review)**: The `SBreak` propagation via
`OBroken` is correctly handled by `ExecSeqBreak` for direct breaks. For nested
loops, `OBroken` is consumed by the inner loop (`ExecForBreak` / `ExecWhile*`)
before reaching the outer loop. This follows from the inductive structure but
must be stated explicitly as a case that was verified.

### 8.3 Proof Strategy

**Recommended approach**: prove only the **→ direction**
(`exec st s out → exec st (desugar s) out`), dropping the ← direction.

The ← direction is needed only if the formal model ever goes from desugared
form back to `SFor`. It does not: `pycsl_soundness` operates on the source
`s` (the `SFor` form) and uses `desugar` to produce the target. Only the →
direction is required — analogous to CompCert's forward simulation, which is
sufficient for compiler correctness without requiring full bisimulation.

A one-directional proof cuts the nested induction work roughly in half.
Assess whether the soundness proof truly needs the ← direction before
committing to the full biconditional.

### 8.4 The `exec_preserves_fresh_var` Scope Chain

`ExecForTrue` updates `for_idx` before executing the body. The lemma's
conclusion is about the *body's output state*, not the full for-loop state.
The chain is:

```
st   →(SAssign for_idx 0)→   st1   →(body)→   body_output_state
```

What must be proved: `lookup body_output_state for_idx = lookup st1 for_idx`
(body doesn't modify `for_idx`, so its value is preserved across the body step).
The loop then reads `for_idx` from `body_output_state` before incrementing.

This chain must be stated precisely to avoid a subtle mismatch: the lemma
should compare `for_idx` in `body_output_state` against `st1` (the state
*entering* the body, after initialization), not against `st` (the original
loop state, before initialization).

### 8.5 Test Note (`contract_expr` vs `expr`)

The test `Lemma test_for_sum` in `Tests.v` uses
`CBinOp OpSub (CInt 3) (CVar for_idx)` as the loop variant. `CBinOp` is a
`contract_expr` constructor, not an `expr` constructor. This is correctly typed
(the WP rule for `SFor` takes a variant of type `contract_expr` evaluated by
`eval_z`), but non-obvious. The test should include a comment distinguishing
the WP rule's variant evaluation path from the SOS execution path.

### 8.6 Effort Estimate

| Task | Estimate |
|---|---|
| Add `ExecFor` constructors to Phase3_SOS.v | 2–3h |
| Add `ELength` to Phase1_AST.v, fix `desugar` guard | 2h |
| Prove `exec_preserves_fresh_var` (state-permutation cascade) | 4–6h |
| Prove `desugar_correct` (→ direction only) | 8–12h |
| Lean port of all the above | +8–10h |
| **Total** | **24–33h** |

---

## 9. Execution Plan

### 9.1 Prerequisites

**Blocker for Phase 2**: `bin/infer-invariants-from-contract.sh` does not
exist. This script is referenced in Phase 2 for LLM-assisted loop invariant
inference. Phase 2 is unexecutable until either:
(a) the script is written (spec: given an annotated Python file with
    `requires`/`ensures`/`assigns`, emit `loop invariant` and `loop variant`
    on all loops inside annotated functions; never add requires/ensures/assigns),
(b) or loop invariants are written entirely by hand.

**Blocker for Layer B contracts on `_handle_for_stmt`**: close
`desugar_correct` (see Section 8) before writing the for-loop WP contract.

### 9.2 Phase Ordering

| Phase | Files | Proof source | Layer | Notes |
|---|---|---|---|---|
| **0** | `__init__.py`, `errors.py` | none | infra | Copy only, no contracts |
| **1** | `ir_schema.py` | none | A | 3 dataclasses, 1 loop |
| **2** | `Module3_Weaver.py`, `ConcurrencyChecker.py` | none | A, C | List accumulation |
| **3** | `Module2_Parser.py` | `Phase1_AST.v` / `AST.lean` | A | 53 AST node dataclasses |
| **4** | `Module1_Ingestor.py`, `Module4_SemanticAnalyzer.py` | none / C | A, C | Validators |
| **5** | `Module5_IREmitter.py` | none | A | IR serialization |
| **6** | `pycsl.py` | none | infra | CLI/I/O — mostly no annotation |
| **7a** | `Module6_WhyMLTranspiler.py` | Phase5b_Soundness.v | B | `assigns` frame conditions on all methods (~1h, no desugar_correct dependency) |
| **7b** | `Module6_WhyMLTranspiler.py` | Phase4_WP.v | B | WP rule `requires`/`ensures` for the 8 non-for statement handlers (critical path) |
| **7c** | `Module6_WhyMLTranspiler.py` | Phase4_WP.v, Phase5a_WhileInv.v | B | Loop annotations on all loops in Module6 |
| **7d** | `Module6_WhyMLTranspiler.py` | Phase3b_Desugar.v | B | `_handle_for_stmt` — **blocked on Section 8 completion** |
| **8** | All annotated files | — | — | `pycsl --no-proof` verification pass |
| **9** | — | — | — | Coverage report |

Phase 7a can start before `desugar_correct` is proved (frame conditions do not
depend on it). Phase 7b and 7c can start immediately after 7a. Phase 7d is the
only phase blocked on the desugaring proof.

### 9.3 Tooling

**Phase 1 — Contract annotation (human-written):**
```bash
cp src/pycsl/<file>.py src/self-annotate/rocq/<file>.py
cp src/pycsl/<file>.py src/self-annotate/lean/<file>.py
# Open the relevant proof file (Rocq or Lean)
# For each function implementing a proven WP rule, write the #@ contracts
```

**Phase 2 — Invariant inference (LLM-assisted, requires prerequisite script):**
```bash
./bin/infer-invariants-from-contract.sh src/self-annotate/rocq/<file>.py
./bin/infer-invariants-from-contract.sh src/self-annotate/lean/<file>.py
```

**Phase 3 — Verification:**
```bash
source .venv/bin/activate
python3 src/pycsl/pycsl.py --no-proof src/self-annotate/rocq/<file>.py
python3 src/pycsl/pycsl.py --no-proof src/self-annotate/lean/<file>.py
```

**Layer 3 audit (Why3 spec):**
```bash
why3 prove src/self-annotate/pycsl-wp-spec.mlw -P Alt-Ergo
```

### 9.4 Per-File Contract Guidance

#### `ir_schema.py` — Layer A
```python
#@ class invariant 1 == 1   # \length(self.field) invalid: self.field is not a CNAME (§3.1.8)
#@ loop invariant 0 <= i and i <= n               # validate() loop
#@ loop variant n - i
```

> **Validation:** L1 ✓ · L2 ✓ (SR-1: `i`, `n` must be in Γ_f — declared as `int`-typed before the loop) · L3 ✓
> *(Fixed: `class invariant True` → `class invariant 1 == 1`; `True` is forbidden in `#@` expressions — forbidden-expressions.md.)*

#### `Module2_Parser.py` — Layer A
```python
#@ assigns \nothing   # pure parse functions
# Field type invariants on dataclass constructors (see Phase1_AST.v constructors)
```

> **Validation:** L1 ✓ · L2 ✓ · L3 ✓ — `assigns \nothing` is the correct form for pure functions with no side effects.

#### `Module5_IREmitter.py` — Layer A
```python
#@ ensures 1 == 1  # aspirational: \forall over \result not expressible (§3.1.8, §3.3)
```

> **Validation:** L1 ✓ · L2 ✓ · L3 ✓ — `1 == 1` passes all levels. Aspirational intent documented in comment.

#### `Module6_WhyMLTranspiler.py` — Layers A + B

Six-step annotation process:
1. Copy source from `src/pycsl/Module6_WhyMLTranspiler.py`
2. Read `Phase4_WP.v`: write `assigns` and `ensures` for each statement handler
3. Read `Phase5a_WhileInv.v`: add `#@ loop invariant` / `#@ loop variant` to every `while` loop inside statement handlers
4. Read `Phase5b_Soundness.v`: write the top-level `transpile()` frame condition
5. Read `Phase3b_Desugar.v`: add `#@ requires 1 == 1` to `_handle_for_stmt` and flag the Admitted gap (`"iter_var" in stmt` passes Module4 but fails Why3 — TR-3, G6; use 1 == 1)
6. Run `pycsl --no-proof` and fix any parse errors

---

## 10. Trusted Computing Base

After self-annotation, the TCB for a verified PyCSL run:

| Component | Trust basis |
|---|---|
| Rocq kernel (8.20) | Machine-checked (highest trust) |
| Lean kernel (4.29) | Machine-checked (highest trust) |
| Why3 kernel + SMT solvers | Machine-checked for Why3; empirical for Z3/Alt-Ergo |
| Python interpreter (3.12) | Empirical (battle-tested) |
| PyCSL transpiler (Modules 1–6) | Structurally verified via self-annotation |
| PyCSL contract parser (Module2) | Self-referential bootstrapping — see below |

**Bootstrapping / "trusting trust"**: Module2 parses its own `#@` annotations.
If it has a bug that misparsed annotations, the self-annotation would not detect
it. The structural defence is strong: the formal proofs in Rocq/Lean are
**external** to Python — checked by independent proof assistants, not by PyCSL.
Even if Module2 is buggy, the soundness theorem remains valid because it was
proved independently without going through Python at all. This is stronger than
CompCert's situation: CompCert's extracted OCaml code is *generated by* Coq, so
a Coq extraction bug could affect it. PyCSL's formal proofs involve no
extraction.

---

## 11. Open Research Questions

### Can We Prove Semantic Equivalence?

Layer 1 contracts verify structural properties. They do NOT verify that the
generated WhyML is semantically equivalent to the WP rule. Full equivalence
would require one of:

1. **Extraction**: Generate Python from Rocq/Lean (à la CompCert). Not
   feasible without rewriting PyCSL in Coq's extraction-compatible fragment.
2. **Deep embedding**: Model WhyML string syntax in PyCSL's contract language.
   Would require extending PyCSL with string-level predicates.
3. **Testing**: Run the formal model on concrete inputs and compare against the
   pipeline's output. Pragmatic but not a proof.

Layer 3 (`pycsl-wp-spec.mlw` + `clone` refinement) is the current tractable
answer: it proves semantic equivalence between the Why3 spec and the generated
WhyML, with the spec manually verified to mirror the Rocq arm.

---

## 12. Success Criteria

1. All `src/self-annotate/rocq/*.py` and `src/self-annotate/lean/*.py` files
   pass `pycsl --no-proof`.
2. Module6 contracts in each path clearly trace back to WP rules in the
   respective proof assistant's formalisation (docstring citing proof file and
   line).
3. Rocq-path and Lean-path contracts for `_handle_for_stmt` both explicitly
   acknowledge the `desugar_correct` Admitted/sorry gap and reference Section 8.
   *(Replacing the trivial original criterion 3 — "contracts agree" — which is
   satisfied by construction if the proof content is identical.)*
4. Coverage report documents: which functions are annotated vs. unannotated,
   and why each unannotated function is outside the formal model.
5. At least one annotated file is added to the CI pipeline as a regression test
   (a `Makefile` target or a test in `test-suite/corpus/` that runs
   `pycsl --no-proof` on the annotated copy).
6. `pycsl-wp-spec.mlw` is accepted by `why3 prove` (no type errors).
7. `audit-guide.md` checklist has been run for all 10 WP arms and results
   recorded.

---

## 13. Risk Mitigation

| Risk | Mitigation |
|---|---|
| Proof and implementation diverge | Start with Phase4_WP.v — most direct mapping; flag any divergence as a bug in either the proof or the implementation |
| Rocq and Lean paths produce different contracts | Treat as a cross-check signal; investigate which proof is more precise |
| `desugar_correct` proof takes longer than estimated | Start Phase 7a–7c in parallel; 7d is the only phase blocked |
| Loop invariant inference produces wrong invariants | Human reviews output before verifying; adjust manually |
| `pycsl --no-proof` fails on nested functions | Scope save/restore fix already applied in `Module4_SemanticAnalyzer.py` |
| String-predicate contracts rejected by parser | Mark as aspirational comments; use currently expressible approximations |
| Nested function closure variables (E2) | Module4 `_build_function_scope` walks only the nested function's own body — closure variables from the enclosing scope are not collected into Γ_f (§1.1.2 of static semantics reference). E2 fires on any reference to them. Fix: re-declare closure variables with `Any` type at the top of the nested function body in the annotated copy, with a comment explaining this is for PyCSL scope analysis (SR-5). |
