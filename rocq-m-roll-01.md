# rocq-m-roll-01.md — PyCSL ↔ Rocq Annotation Methodology

## Purpose

This document is the **ground-truth reference** for deriving `#@` contracts in
`src/self-annotate/src/` from the Rocq formal model in `src/formal-semantics/rocq/`.

Before this document existed, annotations were ported mechanically from earlier
(poorly annotated) reference copies. The result: wrong frame conditions
(`assigns \nothing` for functions that demonstrably write to `self`), vacuous
postconditions (`ensures 1 == 1`), and unannotated functions with observable
side effects.

This document:
1. States what the Rocq model captures and what it does not.
2. Defines three contract sources (R / I / T) — every annotation must be traceable.
3. Gives a per-function recipe that applies to any Python function in the pipeline.
4. Works through Module 1 completely as the reference example.
5. Defines the correct coverage metric.

---

## Section 1 — The Rocq Pipeline Model

### What the Rocq model captures

| Phase | Rocq file | What it defines |
|-------|-----------|-----------------|
| 1 | `Phase1_AST.v` | `expr`, `contract_expr` (60+ constructors), `stmt`, `func_spec`, `frame_cond` |
| 2 | `Phase2_State.v` | `state`, `val`, `ghost_state`, `exec_state`, `eval_expr`, `eval_contract` |
| 3 | `Phase3_SOS.v` | `exec : exec_state → stmt → outcome → Prop` — the small-step rules |
| 3b | `Phase3b_DesugarDef.v` | `desugar : stmt → stmt`; `desugar_correct` theorem |
| 4 | `Phase4_WP.v` | `wp` — weakest precondition predicate |
| 5a | `Phase5a_WhileInv.v` | Loop invariant preservation lemmas |
| 5b | `Phase5b_Soundness.v` | `pycsl_soundness` — the end-to-end metatheorem |

**Key types (Phase 1):**

```rocq
(* Runtime expressions — no logical connectives *)
Inductive expr : Type :=
  | EInt (n : Z) | EVar (x : ident) | ESubscript (arr i : expr)
  | ELen (arr : expr) | EBinOp (op : binop) (e1 e2 : expr) | ENeg (e : expr).

(* Contract expressions — full logical language *)
Inductive contract_expr : Type :=
  | CVar (x : ident) | CResult | COld (e : contract_expr)
  | CEq | CLt | CLe | CGt | CGe | CNe  (* comparisons *)
  | CAnd | COr | CNot | CImplies       (* logical connectives *)
  | CForall | CExists (x : ident) (e : contract_expr)
  | CLength | CSubscript | ...         (* 60+ constructors total *)

(* Frame condition — models #@ assigns *)
Inductive frame_cond : Type :=
  | FNothing              (* assigns \nothing *)
  | FVars (xs : list ident).

(* Complete function specification — one per annotated function *)
Record func_spec := mkSpec {
  spec_pre      : contract_expr;         (* #@ requires *)
  spec_post     : contract_expr;         (* #@ ensures  *)
  spec_frame    : frame_cond;            (* #@ assigns  *)
  spec_variant  : option contract_expr;  (* #@ variant  *)
  spec_trusted  : bool;                  (* #@ \trusted *)
  ...
}.
```

**Key types (Phase 2):**

```rocq
(* Runtime state — association list *)
Definition state := list (ident * val).
Inductive val := VInt (n : Z) | VArray (a : list Z).

(* Evaluation — total, returns VInt 0 on undefined *)
Fixpoint eval_expr (st : state) (e : expr) : val := ...

(* Contract evaluation — logical Prop *)
Definition eval_contract (st pre_st : state) (result : option val)
    (e : contract_expr) : Prop := ...
```

**The SOS relation (Phase 3):**

```rocq
Inductive exec : exec_state → stmt → outcome → Prop :=
  | ExecAssign  : ...
  | ExecAssert  : eval_contract es.reg_state es.reg_state None cond → exec es (SAssert cond msg) (ONormal es)
  | ExecGhostDecl : exec es (SGhostDecl x t e) (ONormal (set_ghost es ...))
  | ExecLabel   : exec es (SLabel L) (ONormal (set_labels es ((L, es.ghost_st) :: es.label_snaps)))
  | ExecWhile   : ...
  | ExecFor     : ...
  ...
```

### What the Rocq model does NOT capture — the Trusted Boundary

**Modules 1, 2, and 3 are outside the formal model.** Rocq assumes `func_spec` is already
constructed — it does not model the process of reading raw `#@` strings from source code,
parsing them, or attaching them to AST nodes.

| Module | Python role | Rocq status |
|--------|-------------|-------------|
| Module 1 | Extract raw `#@` strings from CST | **Trusted** — no Rocq theorem covers it |
| Module 2 | Parse raw strings into `contract_expr` AST | **Trusted** — no Rocq theorem covers it |
| Module 3 | Attach parsed contracts to AST nodes | **Trusted** — no Rocq theorem covers it |
| Modules 4–6 | Semantic analysis, IR emission, WhyML transpilation | Covered by `pycsl_soundness` and WP calculus |

This does NOT mean Modules 1–3 are unannotatable. It means their contracts come from
data-structure invariants and structural guarantees, not from proofs.

---

## Section 2 — Three Contract Sources

Every `#@` annotation MUST be traceable to one of three sources. When writing a contract,
state the source in a comment above the `#@` block.

### Source R — Rocq theorem

A specific Rocq theorem or lemma directly constrains the function's behavior.

**Examples:**
- `visit_FunctionDef` → backs `func_spec` construction (Phase1_AST.v `mkSpec`)
- `visit_While` → backs `SWhile inv var cond body` (Phase3_SOS.v `ExecWhile`)
- `visit_For` → backs `SFor x arr inv var body` and `desugar_correct`
  (Phase3b_DesugarDef.v)
- `visit_SimpleStatementLine` → backs `SGhostDecl`, `SLabel`, `SAssert`
  (Phase3_SOS.v `ExecGhostDecl`, `ExecLabel`, `ExecAssert`)

### Source I — Data-structure invariant

The function manipulates a data structure whose type is modeled in the Rocq AST
(even if the function itself has no theorem). The contract expresses structural
invariants on that data.

**Examples:**
- `PyCSLContract.__init__` → `contracts: List[str]` maps to the list of raw strings
  that will become `list contract_expr`; invariant: length ≥ 0.
- `PyCSLVisitor.__init__` → initializes `extracted_nodes: List[PyCSLContract]` to
  empty; postcondition: length == 0.

### Source T — Trusted boundary

The function is outside the formal model (I/O, CST traversal, external library calls).
It still receives structural contracts capturing frame conditions and output
well-formedness, but these are NOT backed by a proof. Mark them `# Source: T`.

**Examples:**
- `Module1_Ingestor.process` — drives the libcst CST traversal; no Rocq model.
- `_extract_contracts_from_node` — reads libcst node attributes; trusted I/O.
- `visit_Module` — reads module header via libcst API; trusted CST traversal.

---

## Section 3 — The Per-Function Annotation Recipe

Apply this recipe to every `def` in order:

### Step 1 — Write `assigns` first (never skip)

List every `self.X` attribute that can be written by the function.

**Rule:** `assigns \nothing` is only correct when the function provably writes nothing
to any `self` attribute or argument. It must NEVER be used as a default or placeholder.

**Common mistakes caught by this rule:**
- CST visitor methods that append to `self.extracted_nodes` → NOT `\nothing`
- Class `__init__` methods that set `self.X = ...` → NOT `\nothing` (use `\nothing`
  only for `__init__` with no side effects, which rarely exists)
- Helper methods that set `self._header_consumed = True` → assigns `self._header_consumed`

### Step 2 — Write `requires` (when non-trivial)

State what must be true of parameters at entry. Omit if the function accepts anything.

**Standard forms:**
- `requires x != None` — parameter must exist (note: `x is not None` is NOT valid PyCSL syntax)
- `requires \length(xs) >= 0` — list parameter is valid; `xs` must be a plain CNAME
- `requires stmt != None` — IR dict must exist (Module 6 pattern)

### Step 3 — Write `ensures` (never vacuous)

State what is true of the return value and modified state after the call.

**BANNED:** `ensures 1 == 1` — this is a vacuous tautology that proves nothing.

**PyCSL grammar constraints (confirmed by parser):**

```
\length(CNAME)          — CNAME must be a plain variable name; \result is NOT a CNAME
\forall i; expr         — semicolon separator (NOT comma); expr follows
ensures \result != None — valid for any non-void return type
ensures \result != ""   — valid for string-returning functions
ensures self.X != None  — valid for void functions checking a field post-state
ensures self.X == None  — valid for field-reset postconditions
ensures self.flag == False — valid for boolean fields
```

**Standard forms by return type:**

| Return type | `ensures` to use |
|-------------|-----------------|
| `List[X]` | `\result != None` |
| `str` | `\result != ""` if always non-empty; else `\result != None` |
| `None` (void) | `self.X != None` for the key modified field |
| `None` (field reset) | `self.X == None` or `self.flag == False` |
| `Dict` / `Any` | `\result != None` |

**Note on `\old`:** `\old(expr)` is in the grammar (`COld` in Phase1_AST.v) but no existing
verified annotation uses it. Reserve for future work.

**Note on `\length(\result)`:** NOT valid — `\result` is not a `CNAME`. Write
`\result != None` instead. Use `\length(xs)` only when `xs` is a plain parameter name.

### Step 4 — Loop annotations (inside the body)

Every `while` or `for` loop inside a function body MUST have:
```python
#@ loop invariant 0 <= i and i <= n
#@ loop variant n - i
while i < n:
    ...
```

---

## Section 4 — Module 1 Worked Examples

Complete derivation for all 16 definitions in `Module1_Ingestor.py`.

Each entry shows: the function, what it does to state, the source (R/I/T), and
the derived contract.

---

### `PyCSLContract` (dataclass)

**What it is:** Data holder for one annotated Python construct. The `contracts` field
holds raw strings that will become `list contract_expr` when parsed by Module 2.

**Source: I** — mirrors the implicit "list of raw spec strings" preceding `func_spec`
construction in Phase1_AST.v.

```python
# Source: I — contracts is a list of raw strings → list contract_expr (Phase1_AST.v)
#@ class invariant self.contracts != None
#@ class invariant self.node_type != None
#@ class invariant self.node_name != None
class PyCSLContract:
    ...
```

---

### `PyCSLVisitor.__init__`

**What it does:** Sets `self.extracted_nodes = []`, `self._current_class = None`,
`self._module_header_contracts = []`, `self._header_consumed = False`.

**Source: I** — establishes the pre-state for all visitor invariants.

```python
# Source: I — initial state for visitor invariants
#@ assigns \nothing
#@ ensures self.extracted_nodes != None
#@ ensures self._header_consumed == False
def __init__(self) -> None:
```

Note: `assigns \nothing` IS correct here — `__init__` writes to `self` but `self` does
not exist before the call; from the caller's perspective nothing external is modified.

Note on `\length(self.extracted_nodes) == 0`: NOT valid PyCSL syntax — `\length()` only
accepts plain variable names (CNames), not `self.X` dotted expressions. Use
`self.extracted_nodes != None` instead; the emptiness guarantee is implicit (the constructor
sets it to `[]`, which is not None).

---

### `PyCSLVisitor.visit_Module`

**What it does:** Reads `node.header`, appends to `self._module_header_contracts`,
conditionally appends to `self.extracted_nodes`.

**Current annotation (WRONG):** `#@ assigns \nothing`
**Why it's wrong:** The function writes to `self._module_header_contracts` unconditionally,
and to `self.extracted_nodes` when module-level contracts are found.

**Source: T** — libcst module header traversal; no Rocq theorem.

```python
# Source: T — CST traversal; trusted boundary
#@ assigns self.extracted_nodes, self._module_header_contracts
#@ ensures self.extracted_nodes != None
#@ ensures self._module_header_contracts != None
def visit_Module(self, node: cst.Module) -> None:
```

---

### `PyCSLVisitor._extract_contracts_from_node`

**What it does:** Reads `node.leading_lines`, returns raw `#@` strings. Has a
one-time side effect: consumes `self._module_header_contracts` on first call
(sets `self._header_consumed = True`).

**Current annotation: NONE**

**Source: T** — libcst node attribute access; trusted boundary.

```python
# Source: T — CST node attribute reader; trusted boundary
#@ assigns self._module_header_contracts, self._header_consumed
#@ ensures \result != None
def _extract_contracts_from_node(self, node: cst.CSTNode) -> List[str]:
```

---

### `PyCSLVisitor.visit_ClassDef`

**What it does:** Sets `self._current_class = node.name.value`; conditionally
appends to `self.extracted_nodes`.

**Current annotation (WRONG):** `#@ assigns \nothing`

**Source: I** — `ClassDef` annotations carry class invariants modeled in Phase1_AST.v.

```python
# Source: I — class invariant extraction (Phase1_AST.v class invariant)
#@ assigns self.extracted_nodes, self._current_class
#@ ensures self.extracted_nodes != None
def visit_ClassDef(self, node: cst.ClassDef) -> None:
```

---

### `PyCSLVisitor.leave_ClassDef`

**What it does:** Sets `self._current_class = None`.

**Current annotation (WRONG):** `#@ assigns \nothing`

**Source: I** — restores class tracking state.

```python
# Source: I — resets class scope tracker
#@ assigns self._current_class
#@ ensures self._current_class == None
def leave_ClassDef(self, node: cst.ClassDef) -> None:
```

---

### `PyCSLVisitor.visit_FunctionDef`

**What it does:** Calls `_extract_contracts_from_node`, conditionally appends to
`self.extracted_nodes`. The extracted contracts will populate a `func_spec` record.

**Current annotation (WRONG):** `#@ assigns \nothing`

**Source: R** — function contracts are the direct input to `func_spec` construction
(Phase1_AST.v `mkSpec`). The contracts extracted here become `spec_pre`, `spec_post`,
`spec_frame` in the Rocq model.

```python
# Source: R — func_spec population (Phase1_AST.v mkSpec)
# Rocq: func_spec carries spec_pre / spec_post / spec_frame (Phase1_AST.v lines 80–90)
#@ assigns self.extracted_nodes
#@ ensures self.extracted_nodes != None
def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
```

---

### `PyCSLVisitor.visit_While`

**What it does:** Extracts loop invariant/variant contracts from the while node's
leading lines. These become `SWhile inv var cond body` arguments.

**Current annotation (WRONG):** `#@ assigns \nothing`

**Source: R** — loop invariant / variant annotations feed `SWhile inv var cond body`
in Phase3_SOS.v (`ExecWhile`).

```python
# Source: R — SWhile inv var construction (Phase3_SOS.v ExecWhile)
# Rocq: SWhile inv var cond body — inv and var are contract_expr
#@ assigns self.extracted_nodes
#@ ensures self.extracted_nodes != None
def visit_While(self, node: cst.While) -> None:
```

---

### `PyCSLVisitor.visit_For`

**What it does:** Extracts loop invariant/variant for `for` loops. These feed into
`SFor x arr inv var body`, which is desugared to `SWhile` by `desugar`.

**Current annotation (WRONG):** `#@ assigns \nothing`

**Source: R** — `SFor` desugaring (Phase3b_DesugarDef.v `desugar`; `desugar_correct`).

```python
# Source: R — SFor desugaring (Phase3b_DesugarDef.v desugar, desugar_correct)
#@ assigns self.extracted_nodes
#@ ensures self.extracted_nodes != None
def visit_For(self, node: cst.For) -> None:
```

---

### `PyCSLVisitor.visit_With`

**What it does:** Extracts `acquires` / `releases` / `critical` annotations from
`with` blocks (concurrency annotations).

**Current annotation (WRONG):** `#@ assigns \nothing`

**Source: T** — `with` blocks map to mutex semantics; trusted boundary (no Rocq
model for the concurrency extension).

```python
# Source: T — concurrency annotation extraction; trusted boundary
#@ assigns self.extracted_nodes
#@ ensures self.extracted_nodes != None
def visit_With(self, node: cst.With) -> None:
```

---

### `PyCSLVisitor.visit_SimpleStatementLine`

**What it does:** Extracts contracts before simple statements — these are inline
ghost declarations, labels, and asserts that map to `SGhostDecl`, `SLabel`,
`SAssert` in the SOS.

**Current annotation (WRONG):** `#@ assigns \nothing`

**Source: R** — `SGhostDecl` (ExecGhostDecl), `SLabel` (ExecLabel), `SAssert`
(ExecAssertPass / ExecAssertFail) in Phase3_SOS.v.

```python
# Source: R — SGhostDecl / SLabel / SAssert extraction (Phase3_SOS.v ExecGhostDecl, ExecLabel, ExecAssert)
#@ assigns self.extracted_nodes
#@ ensures self.extracted_nodes != None
def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine) -> None:
```

---

### `PyCSLVisitor.visit_IndentedBlock`

**What it does:** Reads `node.footer` to capture trailing `#@` annotations at the
end of an indented block — ghost assignments that appear after the last statement
in a loop body, mapping to `SGhostAssign`.

**Current annotation: NONE**

**Source: R** — trailing ghost annotations inside loop bodies feed `SGhostAssign`
(Phase3_SOS.v).

```python
# Source: R — trailing SGhostAssign inside loop body (Phase3_SOS.v)
#@ assigns self.extracted_nodes
#@ ensures self.extracted_nodes != None
def visit_IndentedBlock(self, node: cst.IndentedBlock) -> None:
```

---

### `Module1_Ingestor.__init__`

**What it does:** Sets `self.source_code = source_code`.

**Source: I** — establishes the input to the ingestion pass.

```python
# Source: I — input initialization
#@ assigns \nothing
#@ ensures self.source_code != None
def __init__(self, source_code: str) -> None:
```

---

### `Module1_Ingestor.process`

**What it does:** Parses `self.source_code` into a libcst CST, runs the visitor,
returns the list of `PyCSLContract` objects.

**Current annotation (WRONG):** `#@ ensures 1 == 1` — vacuous.

**Source: T** — full ingestion pass; trusted boundary; no Rocq theorem covers this.

```python
# Source: T — full CST ingestion pass; trusted boundary
#@ assigns \nothing
#@ ensures \result != None
def process(self) -> List[PyCSLContract]:
```

Note: `\length(\result)` and `\forall i, ...` with `\result` are NOT valid — `\result` is not
a CNAME and cannot appear inside `\length()`. The stronger postcondition
`∀ i, 0 ≤ i < |result| ⟹ result[i] ≠ None` cannot be expressed in the current grammar.
`\result != None` is the best achievable postcondition for a list-returning function.

---

## Section 5 — The Correct Coverage Metric

A function is **correctly annotated** if and only if ALL of:

1. **`assigns` is accurate**: not `\nothing` for any function that writes to `self`.
2. **`ensures` is non-vacuous**: not `1 == 1`; not `\result != None` for void functions (meaningless — void functions have no `\result`); use `self.X != None` for the key modified field.
3. **Source is identifiable**: R, I, or T — findable by inspection.

### Current state (honest count, post porting-script)

| Module | Total defs | Has any `#@` | Correctly annotated | Quality coverage |
|--------|-----------|-------------|---------------------|-----------------|
| Module1 | 16 | 9 | 3 | 19% |
| Module2 | 193 | ~99 | ~50 | 26% |
| Module3 | 11 | 7 | ~4 | 36% |
| Module4 | 32 | 7 | ~5 | 16% |
| Module5 | 131 | 19 | ~15 | 11% |
| Module6 | 152 | 58 | ~40 | 26% |
| **Total** | **535** | **199** | **~117** | **22%** |

The 469 `#@` line count from `grep` is misleading: it includes wrong frame conditions
and vacuous postconditions.

### Priority order for the annotation push

1. **Module 1** (16 defs) — fix now; this document is the recipe.
2. **Module 6** — fix wrong `assigns \nothing` on state-modifying handlers.
3. **Module 4** — well-formedness validators; Source I / Source R from `exec` premises.
4. **Module 5** — IR emitters; Source R from `exec` constructors in Phase3_SOS.v.
5. **Module 2** — parser + AST constructors; Source I from Phase1_AST.v types.
6. **Module 3** — weaver; Source T with structural postconditions.

---

## Section 6 — Quick Reference Card

### Annotation templates by function role

**Pure CST reader (no side effects):**
```python
#@ assigns \nothing
#@ ensures \result != None
def helper(self, node) -> List[str]:
```

**Append-only accumulator (void, writes to one list):**
```python
#@ assigns self.extracted_nodes
#@ ensures self.extracted_nodes != None
def visit_X(self, node) -> None:
```

**Accumulator with class tracking (writes to two fields):**
```python
#@ assigns self.extracted_nodes, self._current_class
#@ ensures self.extracted_nodes != None
def visit_ClassDef(self, node) -> None:
```

**State reset (void, writes to one field):**
```python
#@ assigns self._current_class
#@ ensures self._current_class == None
def leave_ClassDef(self, node) -> None:
```

**Full ingestion pass (returns list):**
```python
#@ assigns \nothing
#@ ensures \result != None
def process(self) -> List[PyCSLContract]:
```
(Stronger element-wise postconditions are not expressible in the current grammar —
`\result` is not a CNAME so `\length(\result)` and `\forall i; ... \result[i] != None`
are both parse errors.)

### Rule: When does `assigns \nothing` apply?

`assigns \nothing` is correct ONLY for:
- `__init__` methods (self doesn't exist before the call)
- Truly pure functions that compute from arguments without touching any field
- Static methods / module-level functions with no state

It is WRONG for: any visitor method, any method that appends to a list field, any method
that sets a field to a new value.
