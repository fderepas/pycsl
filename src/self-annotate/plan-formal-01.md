# Deriving PyCSL Contracts from Formal Proofs — Methodology

**Companion documents:** `self-annotate-global-plan.md`, `audit-guide.md`,
`pycsl-wp-spec.mlw`, `semantic-ceiling.md`

**Target files:** `src/self-annotate/src/*.py` (unannotated source copies)

---

## 1. Directory Roles

```
src/self-annotate/
    src/        ← unannotated copies of src/pycsl/*.py (baseline, no #@ lines)
    rocq/       ← annotated copies; contracts derived from Rocq proofs
    lean/       ← annotated copies; contracts derived from Lean proofs
src/formal-semantics/
    rocq/       ← Phase1_AST.v … Phase5b_Soundness.v
    lean/PyCSL/ ← AST.lean … Soundness.lean
```

Annotating `src/self-annotate/src/` means producing one of the `rocq/` or `lean/`
copies by following this document's methodology.

---

## 2. The Trust Chain

```
Layer 0  Rocq / Lean type-checkers
         Machine-checked soundness theorem: pycsl_soundness
               ↓  [human-audited translation — THIS document]
Layer 1  PyCSL #@ contracts on the Python source
         Structural faithfulness: frame conditions, loop termination,
         WP arm dispatch
               ↓  [machine-checked by pycsl --no-proof]
Layer 2  Why3 + SMT solvers
         Verify the contracts are internally consistent
               ↓  [human-audited link: ensures mirrors Rocq arm]
Layer 3  pycsl-wp-spec.mlw
         One val per WP arm; ensures mirrors Phase4_WP.v exactly.
         Machine-checked (Z3): assign_code_state_coherent lemma.
```

Layer 1 is where THIS document operates. Its contracts are **structurally
weaker** than Layer 3: they capture frame conditions and non-empty output,
not full semantic equivalence. Both layers are necessary and complementary.

---

## 3. The Fundamental Asymmetry

The formal proofs reason about:
- State as `list (ident × val)` — a mathematical association list
- AST nodes as inductive types: `SAssign`, `SWhile`, `EVar`, …
- Pure total functions: `eval_expr st e` always returns a `val`
- A `Fixpoint` over `stmt` — recursive, structural

The Python implementation uses:
- State as Python `dict`, thread-local variables, `self._*` fields
- IR nodes as `Dict[str, Any]` JSON objects
- String building: `f"let {x} = ref {v} in"`, accumulator strings
- `if/elif/else` chains, iteration, mutable accumulators

**There is no syntactic correspondence.** The translation is methodological:
for each Python function, identify its *formal correspondent*, extract the
*logical content*, and encode it as `#@` annotations.

---

## 4. Formal Correspondent Lookup

For each Python function, the formal correspondent answers: "which definition
in the formal model would be INCORRECT if this Python function were wrong?"

| Python function | Formal correspondent | Proof file | Lines |
|---|---|---|---|
| `Module2_Parser.py` dataclasses | `stmt`, `expr`, `contract_expr` inductives | `Phase1_AST.v` / `AST.lean` | `Phase1_AST.v:1–80` |
| `Module5_IREmitter._py_stmts_to_ir` | `exec st s out` premise (output IR is valid `stmt`) | `Phase3_SOS.v` / `SOS.lean` | `Phase3_SOS.v:1–50` |
| `Module6._expr_to_whyml` | `eval_expr`, `eval_bool`, `eval_z` (total, pure) | `Phase2_State.v` / `State.lean` | `Phase2_State.v:50–120` |
| `Module6._stmts_to_whyml` | `exec_deterministic` (same input → same output) | `Phase3_SOS.v` | `:85–110` |
| `Module6._handle_assign_stmt` | `wp (SAssign x e) Q := [x ↦ eval_expr st e] Q` | `Phase4_WP.v` | `:23–24` |
| `Module6._handle_aug_assign_stmt` | `wp (SAugAssign x op e) Q` | `Phase4_WP.v` | `:26–30` |
| `Module6._handle_if_stmt` | `wp (SIf cond s1 s2) Q` | `Phase4_WP.v` | `:41–43` |
| `Module6._handle_while_stmt` | `wp (SWhile inv var cond body) Q` — 3 conjuncts | `Phase4_WP.v` | `:45–66` |
| `Module6._handle_for_stmt` | `desugar` (**blocked** — `desugar_correct` Admitted) | `Phase3b_Desugar.v` | `:73–81` |
| `Module6._handle_return_stmt` | `wp (SReturn e) Q := Qr (update st "\result" ...)` | `Phase4_WP.v` | `:96–97` |
| `Module6._handle_continue_stmt` | `wp SContinue Q := Qc st` | `Phase4_WP.v` | `:99–100` |
| `Module6.transpile` | `pycsl_soundness` (top-level metatheorem) | `Phase5b_Soundness.v` | global |
| All loops in Module6 | `while_inv_preserved` | `Phase5a_WhileInv.v` | global |
| `Module1_Ingestor`, `Module3_Weaver` | No formal correspondent — infrastructure | — | — |
| `Module4_SemanticAnalyzer` | `exec st s out` premise (well-formedness check) | `Phase3_SOS.v` | `:1–20` |
| `ConcurrencyChecker` | Not in formal model | — | — |

---

## 5. The Five Translation Steps

For each function with a formal correspondent:

### Step 1 — Read the Rocq / Lean definition

Open the proof file and locate the definition or fixpoint arm. For Layer B
functions (WP handlers), look at `Phase4_WP.v`. For Layer A functions
(structural preservation), look at `Phase3_SOS.v` or `Phase2_State.v`.

Example for `_handle_assign_stmt`:
```coq
(* Phase4_WP.v:23-24 *)
| SAssign x e =>
    Qn (update st x (eval_expr st e))
```

### Step 2 — Extract the `requires`

The Rocq arm's type assumptions become `requires`. Ask: "What must the input
satisfy for the formal model's precondition to hold?"

For `SAssign`, the IR node must be a non-null dict with a "target" key. Since
PyCSL cannot express dict key membership on unannotated `dict` types (TR-3,
G6), use the typed approximation:
```python
#@ requires stmt != 0
```

For Module5 list parameters, the formal model assumes `s` is a well-formed
`stmt` list:
```python
#@ requires \length(stmts) >= 0
```

For pure functions (Module2, Module3), no precondition is needed beyond
Python's type system:
```python
#@ requires 1 == 1
```

### Step 3 — Extract the `assigns`

The formal `Fixpoint` is pure (no side effects). The Python implementation
is NOT — it maintains mutable `self._*` accumulators. The `assigns` clause
makes explicit which accumulators this function touches.

**Derivation rule:** The `assigns` clause must list ALL `self._*` fields that
could be written. This is derived by reading the Python body — the formal
model gives no information about it.

Standard WP-handler frame (from reading the Python body):
```python
#@ assigns self._known_collection_sizes, self._known_collection_elements
#@ assigns self._array_locals, self._dict_locals, self._lambda_locals
#@ assigns self._record_locals, self._abstract_ops
```

Extended set for loop-handling methods:
```python
#@ assigns self._havoc_counter, self._in_spec
```

For pure Module2/Module3 functions:
```python
#@ assigns \nothing
```

**Note (Hoare model):** In PyCSL's default Hoare model, `assigns self._*`
generates NO WhyML `writes` clause (TR-4). The clause passes Module4 and is
accepted by Why3, but produces no frame proof obligation. Its purpose is
documentation and human auditability.

### Step 4 — Extract the `ensures`

The formal model's output guarantee becomes `ensures`. The full WP guarantee
is expressible at Layer 3 (`pycsl-wp-spec.mlw`):
```why3
ensures { result = update st x e_val }
```

Layer 1 can only express a structural approximation because `\result` is a
`str` in Python and PyCSL maps strings to `int` (TR-2). The standard
approximation is:
```python
#@ ensures \result != ""
```

For handlers that return `str`, `\result != ""` is the maximum expressible
guarantee. For pure `assigns \nothing` functions, use `ensures 1 == 1`.

**Ghost output tags (Layer 1 strengthening):** For WP handlers, add ghost
variables to assert which code branch was taken, proving exhaustive dispatch:
```python
#@ ensures _assign_form == 1 or _assign_form == 2 or _assign_form == 3
def _handle_assign_stmt(...):
    #@ ghost _assign_form = 0
    ...
    if target in self._shared_var_names:
        #@ ghost _assign_form = 3
    ...
    if target not in declared_refs:
        #@ ghost _assign_form = 1
    else:
        #@ ghost _assign_form = 2
```

### Step 5 — Verify

```bash
source .venv/bin/activate
python3 src/pycsl/pycsl.py --no-proof src/self-annotate/rocq/<file>.py
```

Fix any Module4 static-semantics errors (SR-1 through SR-6) or Module5/6
WhyML generation errors (TR-1 through TR-6) before proceeding to the next file.

---

## 6. Three Contract Layers in Detail

### Layer A — Structural Preservation (Modules 1–5, ConcurrencyChecker)

These contracts do not trace back to a specific WP theorem. They follow from the
pipeline's data structure invariants: "data passes through without corruption."

Pattern:
```python
#@ requires \length(stmts) >= 0    # list parameter is non-negative-length
#@ assigns \nothing                 # pure parse/transform function
#@ ensures 1 == 1                  # aspirational — structural result not expressible
```

Use `1 == 1` as `ensures` when the postcondition would require `\length(\result)`
or `\forall` over `\result` — both are invalid because `\result` is not a CNAME
(IS-2, §3.1.8 of the static semantics reference).

### Layer B — WP Rule Correctness (Module6 `_handle_*` methods)

Each WP arm maps to one Python handler. The contract components:

1. `requires` — IR node structural validity (`stmt != 0`)
2. `assigns` — frame condition listing all mutable `self._*` fields
3. `ensures` — output is non-empty (`\result != ""`)
4. (optional) ghost output tags: `_handler_form == N` for dispatch verification

The full WP semantic guarantee (state transformation) lives in Layer 3
(`pycsl-wp-spec.mlw`), not Layer 1. This is the intentional Layer 1/Layer 3 split.

### Layer C — Well-formedness (Module4)

Module4 validates the preconditions assumed by the formal model: variables are
in scope, mutex references are valid, class invariants are well-scoped. These
correspond to the `exec st s out` premise of `pycsl_soundness`.

Pattern:
```python
#@ assigns self.warnings, self._errors
#@ ensures 1 == 1
```

---

## 7. Expressibility Constraints (Mandatory Reading Before Annotating)

PyCSL contracts have hard constraints. Violations may pass `pycsl --no-proof`
but FAIL Why3 (Level 3 silent failures).

| Constraint | Rule | Violation | Correct form |
|---|---|---|---|
| `\result` not a CNAME | IS-2 / §3.1.8 | `\length(\result)` | Not expressible — use `1 == 1` |
| `\forall` over `\result` | §3.3 | `\forall i; \result[i] >= 0` | Not expressible |
| `None` forbidden in `#@` | §1.1 | `ensures \result != None` | `ensures \result != 0` |
| `True`/`False` forbidden | §1.1 | `requires True` | `requires 1 == 1` |
| Dict membership on untyped param | TR-3 / G6 | `"key" in stmt` (unannotated `dict`) | `stmt != 0` |
| `%` / `//` forbidden | §4.1 | `ensures n % 2 == 0` | Not expressible |
| `self.field` in `\length` | IS-2 | `\length(self._list)` | Not expressible — skip |
| Blank line before `def` | Module3 | `#@\n\ndef f():` | No blank lines between last `#@` and `def` |

Full list: `config/skills/pycsl-annotate/references/forbidden-expressions.md`

---

## 8. Per-File Action Table

### `__init__.py` — No annotation

Empty module. Copy verbatim.

### `errors.py` — No annotation

Exception class definitions. Outside the formal model (§7 of global plan).
Copy verbatim.

### `ir_schema.py` — Layer A

```python
# validate() method:
#@ requires 1 == 1
#@ assigns \nothing
#@ ensures 1 == 1

# Any explicit while/for loop:
#@ loop invariant 0 <= i and i <= n
#@ loop variant n - i
```

Formal correspondent: `Phase1_AST.v` constructor types (well-formed IR schema).
Dataclass `#@ class invariant` annotations are blocked by a libcst line-number
mismatch on `@dataclass` classes (§6.1 of global plan).

### `Module1_Ingestor.py` — Layer A

```python
# Main ingest/parse entry points:
#@ requires 1 == 1
#@ assigns self._contracts    # (or \nothing if truly pure)
#@ ensures 1 == 1

# libcst visit_* methods: unannotated (§7 — no formal correspondent)
```

### `Module2_Parser.py` — Layer A

```python
# All 53 AST node dataclasses and parser methods:
#@ requires 1 == 1
#@ assigns \nothing
#@ ensures 1 == 1
```

Formal correspondent: `Phase1_AST.v` inductive constructors. `assigns \nothing`
follows from all `Phase1_AST.v` constructors being pure.

### `Module3_Weaver.py` — Layer A

```python
# CST visitor entry points and weave():
#@ requires 1 == 1
#@ assigns \nothing
#@ ensures 1 == 1
```

No formal correspondent — infrastructure. `assigns \nothing` because weaving
is a pure CST transform.

### `Module4_SemanticAnalyzer.py` — Layer C

```python
# Public visit_* methods:
#@ requires 1 == 1
#@ assigns self._errors
#@ ensures 1 == 1
```

Formal correspondent: `exec st s out` premise validation in `Phase3_SOS.v`.

### `Module5_IREmitter.py` — Layer A

```python
# emit_function, emit_statement, _py_stmts_to_ir, etc.:
#@ requires \length(stmts) >= 0   # where stmts is a list parameter
#@ assigns \nothing
#@ ensures 1 == 1

# Any explicit while/for loop:
#@ loop invariant 0 <= i and i <= n
#@ loop variant n - i
```

Formal correspondent: `Phase3_SOS.v` (output IR must be valid `stmt`).

### `ConcurrencyChecker.py` — Layer A

```python
# check(), _check_function(), _walk_body(), _walk_stmt(), _warn_if_unprotected():
#@ requires 1 == 1
#@ assigns self.warnings
#@ ensures 1 == 1

# summary():
#@ requires 1 == 1
#@ assigns \nothing
#@ ensures 1 == 1
```

No formal correspondent — infrastructure pass outside the formal model.

### `pycsl.py` — Minimal

```python
# _resolve_direct_imports():
#@ \trusted
#@ ensures 1 == 1
```

All other functions are CLI/I/O (§7 of global plan) — leave unannotated.

### `Module6_WhyMLTranspiler.py` — Layers A + B (critical)

Follow the six-step process in §9.4 of the global plan:

**Step 7a — Frame conditions (assigns on every annotatable method):**

```python
# Standard set for all _handle_* methods (from reading the Python body):
#@ assigns self._known_collection_sizes, self._known_collection_elements
#@ assigns self._array_locals, self._dict_locals, self._lambda_locals
#@ assigns self._record_locals, self._abstract_ops

# Extended set for _handle_while_stmt, _handle_for_stmt:
#@ assigns self._havoc_counter, self._in_spec
```

**Step 7b — WP rule contracts (Phase4_WP.v → requires + ensures):**

```python
# _handle_assign_stmt (Phase4_WP.v:23-24)
# wp (SAssign x e) Q := [x ↦ eval_expr st e] Q
#@ requires stmt != 0
#@ requires \length(rest) >= 0
#@ ensures \result != ""
#@ ensures _assign_form == 1 or _assign_form == 2 or _assign_form == 3
#@ assigns ...

# _handle_aug_assign_stmt (Phase4_WP.v:26-30)
#@ requires stmt != 0
#@ ensures \result != ""
#@ assigns ...

# _handle_if_stmt (Phase4_WP.v:41-43)
#@ requires stmt != 0
#@ ensures \result != ""
#@ assigns ...

# _handle_while_stmt (Phase4_WP.v:45-66 — 3-conjunct WP rule)
# C1: invariant at entry; C2: body preserves inv + decreases var; C3: exit post
#@ requires stmt != 0
#@ ensures \result != ""
#@ assigns ...

# _handle_for_stmt (Phase3b_Desugar.v — desugar_correct Admitted)
#@ requires 1 == 1   # placeholder: desugar_correct not yet proved (§8 global plan)
#@ ensures \result != ""
#@ assigns ...

# _handle_return_stmt (Phase4_WP.v:96-97)
# wp (SReturn e) Q := Qr (update st "\result" (eval_expr st e))
#@ requires stmt != 0
#@ ensures \result != ""
#@ assigns ...

# _handle_continue_stmt (Phase4_WP.v:99-100)
# wp SContinue Q := Qc st
#@ requires stmt != 0
#@ ensures \result != ""
#@ assigns ...

# _expr_to_whyml (Phase2_State.v — eval_expr total + pure)
#@ requires 1 == 1
#@ assigns self._abstract_ops
#@ ensures \result != ""

# _stmts_to_whyml (Phase3_SOS.v — exec_deterministic)
#@ requires \length(stmts) >= 0
#@ assigns self._known_collection_sizes, self._known_collection_elements
#@ assigns self._array_locals, self._dict_locals, self._lambda_locals
#@ assigns self._record_locals, self._has_early_ret
#@ assigns self._abstract_ops, self._havoc_counter
#@ ensures \result != ""

# transpile() (Phase5b_Soundness.v — pycsl_soundness metatheorem)
#@ requires 1 == 1
#@ assigns self._all_record_fields, self._module_func_names
#@ assigns self._bounded_int, self._current_params    # ... all 15 mutable fields
#@ ensures \result != ""
```

**Step 7c — Loop annotations (Phase5a_WhileInv.v → every while loop):**

```python
# For every while loop inside a _handle_* method body:
#@ loop invariant 0 <= i and i <= n
#@ loop variant n - i
```

Replace `i` and `n` with the actual loop counter and bound variable names
(e.g., `i_inv_w`, `n_inv_w` for the invariant-processing loop in
`_handle_while_stmt`).

Formal correspondent: `while_inv_preserved` in `Phase5a_WhileInv.v` — if the
invariant holds at entry and the body preserves it while decreasing the variant,
it holds at exit.

---

## 9. The Proof → Contract Link (Full Example: SAssign)

### Rocq arm (Phase4_WP.v:23-24)

```coq
| SAssign x e =>
    Qn (update st x (eval_expr st e))
```

Mathematical content: after `SAssign x e`, the state is updated at `x` with
the value of expression `e` in the current state `st`.

### What Layer 3 captures (`pycsl-wp-spec.mlw:PyCSL_WP_Spec`)

```why3
val handle_assign (x: ident) (e_val: value) (st: state) : state
  ensures { result = update st x e_val }
```

Direct encoding of the Rocq arm. Machine-checked by Z3.

### What Layer 3 additionally captures (`pycsl-wp-spec.mlw:PyCSL_WP_Code`)

```why3
val function handle_assign_code
    (lhs rhs_str indent rest_str : string) (declared : bool) : string
  ensures { declared ->
    result = concat (concat (concat (concat (concat indent lhs) " := ") rhs_str) ";\n") rest_str }
  ensures { not declared ->
    result = concat ... "let " ... " = ref " ...
    \/ result = concat ... "let " ... " = " ... }
```

String-level encoding of the two binding forms the Python code emits.
Coherence proved: the emitted string implements the state transformation.

### What Layer 1 captures (`#@` annotation)

```python
#@ requires stmt != 0
#@ requires \length(rest) >= 0
#@ ensures \result != ""
#@ ensures _assign_form == 1 or _assign_form == 2 or _assign_form == 3
#@ assigns self._known_collection_sizes, ...
```

Structural approximation:
- `ensures \result != ""` ≈ "the function produced SOME output" (not: the
  output implements `update`)
- Ghost tag `_assign_form` ≈ "the function chose the correct branch" (not:
  the branch is semantically correct)
- `assigns` clause ≈ "these are all the mutable fields touched" (not: the
  state transform is exact)

The gap from Layer 1 to Layer 3 is documented in `semantic-ceiling.md`.

### Why both layers are needed

| Property | L1 `#@` | L3 `pycsl-wp-spec.mlw` |
|---|---|---|
| Frame conditions (assigns) | ✓ | — |
| Loop termination | ✓ | — |
| Branch exhaustiveness (ghost tags) | ✓ | — |
| Non-empty output | ✓ | — |
| Semantic WP equivalence | — | ✓ |
| String structure (let/ref forms) | — | ✓ (`PyCSL_WP_Code`) |
| Coherence (string → state) | — | ✓ (`PyCSL_WP_Coherence`) |

---

## 10. Execution Plan (Prioritized Order)

| Priority | File | Layer | Effort | Notes |
|---|---|---|---|---|
| 1 | `errors.py`, `__init__.py` | — | 5 min | copy only |
| 2 | `ir_schema.py` | A | 15 min | 1 validate() + loops |
| 3 | `Module2_Parser.py` | A | 1h | 53 AST node classes, all `assigns \nothing` |
| 4 | `Module3_Weaver.py`, `ConcurrencyChecker.py` | A | 30 min | small files |
| 5 | `Module1_Ingestor.py`, `Module4_SemanticAnalyzer.py` | A/C | 1h | Layer A/C |
| 6 | `Module5_IREmitter.py` | A | 1h | 38 target annotations |
| 7 | `pycsl.py` | — | 15 min | one `\trusted` |
| 8 | `Module6_WhyMLTranspiler.py` steps 7a–7c | A+B | 4h | critical path |
| 9 | `Module6` step 7d (`_handle_for_stmt`) | B | blocked | pending `desugar_correct` |

**Total estimate:** ~8h for first pass on all files, excluding step 9.

---

## 11. Verification

```bash
source .venv/bin/activate

# Single file
python3 src/pycsl/pycsl.py --no-proof src/self-annotate/rocq/<file>.py

# All rocq/ files
for f in src/self-annotate/rocq/*.py; do
    python3 src/pycsl/pycsl.py --no-proof "$f" \
        && echo "PASS $(basename $f)" \
        || echo "FAIL $(basename $f)"
done

# Layer 3 spec (coherence lemma requires Z3)
why3 prove src/self-annotate/pycsl-wp-spec.mlw -P "Z3,4.13.3,"

# Cross-check rocq/ vs lean/ annotations (should be structurally identical)
diff src/self-annotate/rocq/Module6_WhyMLTranspiler.py \
     src/self-annotate/lean/Module6_WhyMLTranspiler.py \
     | grep "^[<>].*#@"
```

---

## 12. Open Gaps

| Item | Status | Impact |
|---|---|---|
| `desugar_correct` Admitted/sorry | Blocked — §8 of global plan | `_handle_for_stmt` Layer B contract deferred |
| `\length(\result)` not expressible | PyCSL grammar gap | All emitter postconditions use `1 == 1` |
| `\forall` over `\result` | PyCSL grammar gap | Element-wise output checks not expressible |
| Dict key membership in contracts | TR-3/G6 | `"key" in stmt` fails Why3; use `stmt != 0` |
| Semantic WP equivalence at Layer 1 | Out of scope for Layer 1 | Covered by Layer 3 + `semantic-ceiling.md` |

---

Once the plan is done, provide recommendations and draft a new plan in `./src/self-annotate/src/plan-formal-??.md` where ?? is a new number compared to existing ones.