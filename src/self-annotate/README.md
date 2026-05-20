# Self-Annotating PyCSL: From Formal Proofs to `#@` Contracts

## Overview

PyCSL's formal soundness theorem (`pycsl_soundness`) is machine-checked in both
Rocq and Lean. That proves the *mathematics* is correct. The remaining trust gap:
does the *Python implementation* faithfully realize those mathematics?

This directory closes that gap by annotating the PyCSL implementation
(`src/pycsl/*.py`) with its own `#@` contract syntax, then verifying the
annotations with Why3. The annotated copies live in:

```
src/self-annotate/rocq/    ← contracts derived from Rocq proofs
src/self-annotate/lean/    ← contracts derived from Lean proofs
```

Both paths annotate the same source files. If their contracts agree, confidence
in both the proofs and the implementation is higher.

---

## Related Documents

| Document | Purpose |
|---|---|
| `self-annotate-plan.md` | Main execution plan: phases, tooling, success criteria |
| `self-annotate-plan-to-contract.md` | Translation methodology: how proofs become `#@` annotations |
| `self-annotate-plan-no-sugar.md` | Sub-plan: closing the `desugar_correct` Admitted/sorry |
| `self-annotate-comments-from-Claude.md` | Review: 17 issues across the three plan documents |
| `self-annotate-layer3/README.md` | Layer 3: Why3 `val` spec module — machine-checked WP equivalence |
| `self-annotate-layer3/audit-guide.md` | Global audit guide: Rocq theorem → PyCSL `#@` annotation |

---

## Trust Chain

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

Layer 3 — Why3 val spec module  (self-annotate-layer3/pycsl-wp-spec.mlw)
   Semantic equivalence: one val per WP arm, ensures clause mirrors
   the Rocq fixpoint arm exactly.
   Machine-checked: Why3 clone/refinement proves generated code satisfies spec.
   Human-audited:   val spec written by inspection of Phase4_WP.v (line-by-line).
   See self-annotate-layer3/audit-guide.md for the full audit procedure.
```

Each layer covers what the others cannot:
- Layer 0 proves the WP calculus is mathematically sound.
- Layer 1 proves the Python code doesn't silently drop statements,
  corrupt state, or diverge from the formal structure.
- Layer 2 proves the actual generated WhyML satisfies the VCs.

---

## The Fundamental Asymmetry

The formal proofs reason about:
- State as `list (ident × val)` — a mathematical association list
- Expressions as inductive types: `EInt`, `EVar`, `EBinOp`, …
- Total, pure functions (`eval_expr` returns `VInt 0` on out-of-bounds)
- The WP calculus as a fixpoint over inductive `stmt`

The Python implementation uses:
- State as Python dicts
- IR as JSON objects (not inductive types)
- String building for WhyML output
- `if/elif` chains, not recursive fixpoints

There is no 1:1 syntactic correspondence. The translation is methodological:
for each Python function, identify its *formal correspondent*, extract the
*logical content* of the relevant theorem, then encode it as `#@` annotations
capturing what PyCSL's contract language can express.

---

## What Can and Cannot Be Expressed

**PyCSL contracts can assert:**
- Frame conditions: `#@ assigns self._known_collection_sizes, …`
- Non-emptiness: `#@ ensures \result != ""`
- Structural invariants: `#@ loop invariant 0 <= i and i <= n`
- Termination: `#@ loop variant n - i`
- Pure functions: `#@ assigns \nothing`
- Element well-formedness: `#@ ensures \forall i, … ==> \result[i] is not None`

**PyCSL contracts cannot currently assert:**
- "The generated WhyML string, when parsed, represents `SAssign(x, e)`."
- Semantic equivalence between Python output and the WP rule.
- String membership predicates such as `"Return" in \result`.

The string-building barrier is fundamental. Layer 2 (Why3) fills this gap:
when the user's program is verified with `pycsl`, Why3 checks the generated
WhyML's semantic content. Layers 1 and 2 together cover what neither can alone.

---

## Three Contract Layers

### Layer A — Structural Preservation (Modules 1–5)

These contracts ensure data is not lost or corrupted through the pipeline.
They do not trace back to a specific theorem; they follow from the pipeline's
data structure invariants.

Examples:
```python
#@ class invariant \length(self.functions) >= 0          # ir_schema.py
#@ assigns \nothing                                       # pure parse functions
#@ ensures \forall i, 0 <= i and i < \length(\result) ==> \result[i] is not None
```

### Layer B — WP Rule Correctness (Module6)

Each arm of the WP fixpoint in `Phase4_WP.v` / `WP.lean` maps to one
handler in `Module6_WhyMLTranspiler.py`. The contract captures the formal
arm's frame condition and structural output requirement.

| WP Rule | Rocq | Handler | Contract pattern |
|---|---|---|---|
| `wp SSkip` | Phase4_WP.v:21 | `"Pass"` branch | `assigns \nothing` |
| `wp SAssign` | Phase4_WP.v:23–24 | `_handle_assign_stmt` | assigns collection tracking state |
| `wp SAugAssign` | Phase4_WP.v:26–30 | inline ~line 1380 | assigns clause |
| `wp SArraySet` | Phase4_WP.v:32–35 | inline | assigns clause |
| `wp SSeq` | Phase4_WP.v:37–39 | `_stmts_to_whyml` (recursive) | `requires \length(stmts) >= 0` |
| `wp SIf` | Phase4_WP.v:41–43 | `"If"` branch ~line 1485 | pure dispatch |
| `wp SWhile` | Phase4_WP.v:45–66 | `_handle_while_stmt` | loop invariant on `i_inv_w`, variant on `i_var_w` |
| `wp SFor` | Phase4_WP.v:68–94 | `_handle_for_stmt` | `requires stmt["iter_var"] != "_pycsl_idx"` |
| `wp SReturn` | Phase4_WP.v:96–97 | `"Return"` branch ~line 1468 | assigns clause |
| `wp SContinue` | Phase4_WP.v:99–100 | `"Continue"` branch ~line 1478 | assigns clause |

The three WP continuations (`Qn`, `Qr`, `Qc`) become:
- `Qn` — string concatenation with `";\n"` in `_stmts_to_whyml`
- `Qr` — WhyML `raise Return` / `try … with Return r -> r end`
- `Qc` — WhyML `raise PyCSL_Continue`

### Layer C — Well-formedness (Module4)

Module4's validators check the preconditions assumed by the formal model
(variables in scope, mutex references valid, class invariants well-scoped).
These correspond to the `exec st s out` premise of `pycsl_soundness` — the
program must be executable for the theorem to apply.

---

## Proof File → Contract Mapping

### `Phase1_AST.v` → `Module2_Parser.py`, `Module5_IREmitter.py`

Defines the grammar of `stmt`, `expr`, `contract_expr`, `func_spec` as
inductive types. Module2's dataclass definitions mirror these constructors.

```python
@dataclass
class Requires:
    #@ class invariant self.expr is not None
    expr: Any
```

For Module5 (IR emitter), each emitted IR node must correspond to a valid
`stmt` or `expr` constructor:
```python
def _py_stmts_to_ir(self, stmts):
    #@ requires stmts is not None
    #@ ensures \forall i, 0 <= i and i < \length(\result) ==> \result[i] is not None
```

### `Phase2_State.v` → `Module6._expr_to_whyml`

Proves `eval_expr`, `eval_bool`, `eval_z`, `eval_contract` are total and
pure. The implementation counterpart accumulates abstract operation
declarations as a side effect:

```python
def _expr_to_whyml(self, expr_ir, local_refs, ...):
    #@ assigns self._abstract_ops    # acknowledges the side effect
    #@ ensures \result is not None
```

The formal model hides abstract-ops behind the `eval_expr` total function.
The contract makes the refinement gap explicit.

### `Phase3_SOS.v` → Frame Conditions on `_stmts_to_whyml`

Proves `exec_deterministic`: same input produces same output. In the
implementation, determinism is captured by the `assigns` clause — the same
input reaches the same mutable fields, so the output is identical:

```python
def _stmts_to_whyml(self, stmts, local_refs, declared_refs, indent, in_loop):
    #@ assigns self._known_collection_sizes, self._known_collection_elements
    #@ assigns self._array_locals, self._dict_locals, self._lambda_locals
    #@ assigns self._record_locals, self._has_early_ret
    #@ assigns self._abstract_ops, self._havoc_counter
    #@ ensures \result is not None
```

### `Phase3b_Desugar.v` → `Module6._handle_for_stmt`

Defines `desugar`, which transforms `SFor x arr inv var body` into an
equivalent `SWhile` using index variable `_pycsl_idx`. The correctness
lemma `desugar_correct` is currently `Admitted` (Rocq) / `sorry` (Lean) —
see `self-annotate-plan-no-sugar.md` for the sub-plan to close this.

The contract for `_handle_for_stmt` captures the freshness precondition:

```python
def _handle_for_stmt(self, stmt, ...):
    #@ requires stmt["iter_var"] != "_pycsl_idx"
    #@ ensures "_pycsl_idx" in \result or "for_idx" in \result
```

**Note**: Because `desugar_correct` is Admitted, the Layer B contract for
`_handle_for_stmt` is the weakest link — it claims formal justification that
is not yet machine-checked.

### `Phase4_WP.v` → All `_handle_*_stmt` Methods

The core translation. Each handler has three contract components:

1. **`requires`** — IR node well-formedness (keys present, types correct)
2. **`assigns`** — frame condition listing all mutable fields modified
3. **`ensures`** — output is non-empty

Example for `_handle_while_stmt`:
```python
def _handle_while_stmt(self, stmt, rest, local_refs, declared_refs, indent, in_loop):
    # Formal correspondent: wp (SWhile inv var cond body) Phase4_WP.v:45-66
    # The WP rule requires:
    #   1. Invariant holds at entry.
    #   2. Body preserves inv and decreases var.
    #   3. When ¬cond, Qn holds.
    #@ requires stmt is not None
    #@ requires "test" in stmt
    #@ assigns self._known_collection_sizes, self._known_collection_elements
    #@ assigns self._array_locals, self._dict_locals, self._lambda_locals
    #@ assigns self._record_locals, self._has_early_ret
    #@ assigns self._abstract_ops, self._havoc_counter, self._in_spec
    #@ ensures \result != ""
```

### `Phase5a_WhileInv.v` → Loop Annotations on `_handle_while_stmt`

Proves `while_inv_preserved`: if the invariant holds at loop entry and the
variant decreases each iteration, the invariant holds at loop exit. This
justifies the existing loop annotations inside `_handle_while_stmt`:

```python
#@ loop invariant 0 <= i_inv_w and i_inv_w <= n_inv_w
#@ loop variant n_inv_w - i_inv_w
while i_inv_w < n_inv_w:
    ...
```

This is the self-referential bootstrap: PyCSL verifies its own loop
annotations using the same methodology that `pycsl_soundness` was proved for.

### `Phase5b_Soundness.v` → Top-Level `transpile()`

The soundness theorem is a *metatheorem* about the contract system — it
is not itself a `#@` annotation. It justifies *why* the Layer B contracts
are correct: if all WP arms are implemented correctly (which the contracts
verify), then the combined system is sound.

It maps to the top-level frame condition on `transpile()`:

```python
def transpile(self):
    # Formal correspondent: pycsl_soundness Phase5b_Soundness.v
    #@ assigns self._all_record_fields, self._module_func_names
    #@ assigns self._bounded_int, self._current_params, ...
    #@ ensures \result is not None
    #@ ensures \length(\result) > 0
```

---

## Six-Step Annotation Process

For each file in `src/pycsl/`:

1. **Copy** the unannotated source:
   ```bash
   cp src/pycsl/<file>.py src/self-annotate/rocq/<file>.py
   cp src/pycsl/<file>.py src/self-annotate/lean/<file>.py
   ```

2. **Read `Phase4_WP.v`** (or `WP.lean`) — identify the WP arm for each
   statement handler. Write the `assigns` and `ensures` contracts.

3. **Read `Phase5a_WhileInv.v`** (or `WhileInv.lean`) — add
   `#@ loop invariant` / `#@ loop variant` to every `while` loop inside
   statement handlers.

4. **Read `Phase5b_Soundness.v`** (or `Soundness.lean`) — write the
   top-level `transpile()` frame condition.

5. **Read `Phase3b_Desugar.v`** (or `DesugarDef.lean` / `Desugar.lean`) —
   add `#@ requires stmt["iter_var"] != "_pycsl_idx"` to `_handle_for_stmt`
   and flag the Admitted gap.

6. **Verify:**
   ```bash
   source .venv/bin/activate
   python3 src/pycsl/pycsl.py --no-proof src/self-annotate/rocq/<file>.py
   python3 src/pycsl/pycsl.py --no-proof src/self-annotate/lean/<file>.py
   ```

For Modules 1–5 (Layer A only), skip steps 2–5 and write structural
contracts directly: `assigns`, `ensures \length(...) >= 0`, loop invariants.

---

## What Is NOT Annotated

Functions outside the formal model are left unannotated. They are NOT
marked `\trusted` — that keyword is reserved exclusively for standard
library stubs in `data/lib_stubs/`.

| Category | Examples |
|---|---|
| I/O and subprocess | `pycsl.py` CLI, file reads |
| libcst CST visitors | `Module1_Ingestor.py` `visit_*` methods |
| Complex string builders | Module6 output string assembly helpers |
| Error/exception classes | `errors.py` |
| JSON parse callsites | `json.loads()` in the pipeline |

---

## Open Gaps

| Gap | Status |
|---|---|
| `desugar_correct` (Admitted/sorry) | Blocked — see `self-annotate-plan-no-sugar.md` |
| Semantic equivalence of generated WhyML | Out of scope for Layer 1; covered by Layer 2 (Why3) |
| String predicate contracts (`"Return" in \result`) | Not expressible in current PyCSL contract language |
| CI integration for annotated files | Recommended but not yet implemented |

The `desugar_correct` gap is the only one that affects soundness claims.
All other gaps affect annotation completeness or expressiveness, not
correctness.

---

## Trusted Computing Base

After self-annotation, the TCB for a verified PyCSL run is:

| Component | Trust basis |
|---|---|
| Rocq kernel (8.20) | Machine-checked (highest trust) |
| Lean kernel (4.29) | Machine-checked (highest trust) |
| Why3 kernel + SMT solvers | Machine-checked for Why3; empirical for Z3/Alt-Ergo |
| Python interpreter (3.12) | Empirical (battle-tested) |
| PyCSL transpiler (Modules 1–6) | Structurally verified via self-annotation |
| PyCSL contract parser (Module2) | Self-referential bootstrapping — mitigated by external Rocq/Lean proofs |

The self-referential nature of Module2 (it parses its own `#@` syntax) is
the classic bootstrapping problem. The mitigation is that the formal proofs
are *external* to Python: even if Module2 misparsed `#@` annotations, the
Rocq/Lean soundness theorem would remain valid because it was checked
independently of the Python implementation.
