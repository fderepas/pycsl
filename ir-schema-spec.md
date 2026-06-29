# ir-schema-spec.md — Typed IR schema refactor to close body-faithful `_handle_*`

**Goal:** replace the `Dict[str, Any]` IR node representation with a typed sum-type schema so that `src/pycsl/module6_whyml/statements.py`'s 12 `_handle_*` methods can be body-faithfully annotated (closing LINK 3 of `formal-semantics-completion.md` §8).

**Status:** Phases A+B COMPLETE; Phase C PARTIAL. The refactor succeeded in the **real codebase** (the 12-method blocker converted from "architectural (can't type-check `Any`)" to "mechanical (typed field access)"), but the **self-annotate isolation** can't yet reap the payoff because pycsl doesn't resolve cross-file type imports — leaving B1 (opaque types) as the dominant residual blocker.

---

## 1. Why the current IR blocks body-faithful annotation

The IR is JSON-shaped `Dict[str, Any]` (`src/pycsl/ir_schema.py` defines `TypedDict` classes for *documentation*, but the runtime values are `Dict[str, Any]` with `Any`-typed — i.e. nested-dict — values). The 12 `_handle_*` methods are dynamic metaprograms over this shape:

```python
def _handle_assign_stmt(self, stmt: Dict[str, Any], ...):
    target = stmt["target"]              # str — OK (str-keyed dict, now supported)
    val_ir = stmt.get("value", {})       # Dict[str, Any] — ANY-typed value
    vt = val_ir.get("type", "")          # subscript on Any → type error
    ...
```

The 6 lowering extensions landed (isinstance, getattr, nested-def, newline-escape, str-accumulation, string-keyed dict) each unblocked a sub-pattern, but the final blocker is architectural: **`stmt["value"]` is `Any`-typed, so `stmt["value"]["type"]` is a subscript on an `Any`-typed value** — PyCSL cannot type-check it without a record/sum-type schema for the IR node shapes.

The same problem recurses: `val_ir.get("elts", [])` is a list of `Any`-typed dicts; `stmt["test"]` is `Any`; `stmt["cond"]`, `stmt["body"]`, `stmt["init"]`, `stmt["step"]` are all `Any`. Every nested IR access is untyped.

---

## 2. The refactor principle

**Replace the open `Dict[str, Any]` with a closed sum type (one constructor per IR node kind), each constructor carrying typed fields.** This is the standard "typed AST" pattern: instead of `{"stmt": "Assign", "target": ..., "value": ...}`, use a `StmtIR` sum with an `AssignStmt(target: str, value: ExprIR)` constructor. Each field has a concrete type; nested accesses are typed.

```
                          BEFORE                              AFTER
   stmt: Dict[str, Any]                                stmt: StmtIR
   stmt["stmt"]  → str  ("Assign")                     stmt.kind  → StmtKind  (enum)
   stmt["target"] → Any                                AssignStmt.target → str
   stmt["value"]  → Any (Dict[str, Any])               AssignStmt.value  → ExprIR (sum)
   stmt["value"]["type"] → Any                         stmt.value.kind   → ExprKind (enum)
```

The key change: **every IR access becomes a typed-field access on a sum constructor**, not a string-keyed `Any`-typed dict lookup. PyCSL can then type-check `stmt.value.kind` (a field access on an `AssignStmt` → `ExprKind` enum), which is exactly what body-faithful annotation needs.

---

## 3. The schema (PyCSL-side: Python dataclasses / sum types)

### 3.1 StmtIR — the sum type for statement nodes

```python
# A closed sum: every IR statement kind is one constructor.
# (The "kind" string becomes an enum; the payload fields are typed.)

class StmtIR:                # base (or use a union / dataclass-with-tag)
    kind: StmtKind

class AssignStmt(StmtIR):
    target: str
    value: "ExprIR"

class AugAssignStmt(StmtIR):
    target: str
    op: BinopKind
    value: "ExprIR"

class ArraySetStmt(StmtIR):
    array: str
    index: "ExprIR"
    value: "ExprIR"

class ArraySliceSetStmt(StmtIR):
    array: str
    lower: "ExprIR"
    upper: Optional["ExprIR"]
    value: "ExprIR"

class IfStmt(StmtIR):
    cond: "ExprIR"
    then_body: List["StmtIR"]
    else_body: List["StmtIR"]

class WhileStmt(StmtIR):
    invariant: List["ContractExprIR"]
    variant: Optional["ContractExprIR"]
    cond: "ExprIR"
    body: List["StmtIR"]

class ForStmt(StmtIR):
    var: str
    iterable: str
    invariant: List["ContractExprIR"]
    variant: Optional["ContractExprIR"]
    body: List["StmtIR"]

class ReturnStmt(StmtIR):
    value: "ExprIR"

class ExprStmt(StmtIR):
    expr: "ExprIR"

class TryStmt(StmtIR):
    body: List["StmtIR"]
    handlers: List["HandlerIR"]

class MatchStmt(StmtIR):
    subject: "ExprIR"
    cases: List["MatchCaseIR"]

class CriticalSectionStmt(StmtIR):
    mutex: str
    body: List["StmtIR"]

class FieldAssignStmt(StmtIR):
    object: str
    field: str
    value: "ExprIR"

class FieldAugAssignStmt(StmtIR):
    object: str
    field: str
    op: BinopKind
    value: "ExprIR"

class TupleUnpackStmt(StmtIR):
    targets: List[str]
    value: "ExprIR"

class GhostAssignStmt(StmtIR):
    target: str
    ghost_type: str
    op: AugOpKind
    value: "GhostExprIR"

class GhostArraySetStmt(StmtIR):
    array: str
    index: "ExprIR"
    value: "GhostExprIR"

class LabelStmt(StmtIR):
    name: str

class RaiseStmt(StmtIR):
    exc_type: str

class AssertStmt(StmtIR):
    kind: str       # "assert" | "check"
    test: "ContractExprIR"
    origin: Optional[str]

class PassStmt(StmtIR): ...
class BreakStmt(StmtIR): ...
class ContinueStmt(StmtIR): ...
class SCallStmt(StmtIR):         # the Lambda closure call (Phase 8)
    result: str
    fn: "ExprIR"
    arg: "ExprIR"
class SAcquiresStmt(StmtIR):
    mutex: str
class SReleasesStmt(StmtIR):
    mutex: str
```

### 3.2 ExprIR — the sum type for expression nodes (same pattern)

`{"type": "BinOp", "op": "Add", "left": ..., "right": ...}` → `BinOpExpr(op: BinopKind, left: ExprIR, right: ExprIR)`. Every `ExprIR` constructor has typed fields; `expr["left"]` becomes `expr.left` (typed `ExprIR`, not `Any`).

### 3.3 ContractExprIR — the sum type for contract-expression nodes

Same pattern: `\forall i. 0 <= i < n -> arr[i] == x` becomes `ForallExpr(var: str, body: ContractExprIR)` with typed sub-nodes.

### 3.4 The dispatch becomes a typed match

The current dispatch:
```python
s_type = stmt["stmt"]
handler = self._STMT_HANDLERS.get(s_type)
if handler: return getattr(self, handler)(stmt, rest, ...)
```
becomes (conceptually):
```python
match stmt:
    case AssignStmt(target, value): return self._handle_assign(target, value, rest, ...)
    case IfStmt(cond, then_body, else_body): return self._handle_if(cond, then_body, else_body, rest, ...)
    ...
```
Each handler receives TYPED fields, not a `Dict[str, Any]` to index into.

---

## 4. WhyML lowering of the typed schema (the keystone for body-faithful)

PyCSL must lower the typed `StmtIR` sum to WhyML so a `_handle_*` method's body type-checks. Two parts:

### 4.1 Model `StmtIR` as a WhyML algebraic data type
For the self-annotate use case, the emitter's `_handle_*` methods take a `StmtIR` and produce a `string`. PyCSL models `StmtIR` as a WhyML variant:
```whyml
type stmt_ir =
  | SAssign   of string expr_ir
  | SIf       of expr_ir (list stmt_ir) (list stmt_ir)
  | SWhile    of (list contract_expr_ir) (option contract_expr_ir) expr_ir (list stmt_ir)
  | SReturn   of expr_ir
  | ...
```
and `ExprIR` / `ContractExprIR` as corresponding variants. (This mirrors the formal model's `Stmt` inductive in `src/formal-semantics/` — the two `Stmt` types align constructor-by-constructor, which is LINK 1 of `formal-semantics-completion.md` §8.)

### 4.2 The `_handle_*` body type-checks
With `StmtIR` a typed sum, the `_handle_assign_stmt` body:
```python
def _handle_assign_stmt(self, stmt: AssignStmt, ...):
    target = stmt.target          # str  — typed field access
    val_ir = stmt.value           # ExprIR — typed (not Any)
    vt = val_ir.kind              # ExprKind enum — typed
    ...
```
becomes a sequence of typed record-field accesses. PyCSL lowers `stmt.target` (field access on `AssignStmt`) to WhyML record-field access `stmt.target`; `val_ir.kind` to `val_ir.kind`. No `Any`, no string-keyed dict, no dynamic subscript on `Any`.

### 4.3 The `match` dispatch lowers to a WhyML `match`
The Python `match stmt: case AssignStmt(...): ...` becomes a WhyML `match stmt with | SAssign target value -> ... end`. Why3's exhaustiveness check fires (same as the Union/Optional match-exhaustiveness lowering from the typing engagement).

---

## 5. Scope — what changes, what doesn't

### In scope
- `src/pycsl/ir_schema.py` — add the typed sum-type classes (StmtIR, ExprIR, ContractExprIR + their constructors). Keep the existing `TypedDict` as a JSON-serialization layer (the wire format stays JSON; the typed sums are the in-memory representation).
- `src/pycsl/frontend/Module5_IREmitter.py` — emit the typed sums instead of `Dict[str, Any]`. The IR JSON serialization converts sums → dicts on output (so `*.ir.json` goldens are unchanged).
- `src/pycsl/module6_whyml/statements.py` (and `expressions.py`, `preamble.py`) — consume the typed sums; the `_handle_*` methods take `StmtIR` subclasses.
- `src/pycsl/module6_whyml/functions.py` — add the `StmtIR`/`ExprIR`/`ContractExprIR` WhyML variant declarations (the emitter's model of its own input).
- `src/self-annotate/src/module6_whyml/statements.py` — re-annotate body-faithful (the 12 `_handle_*` methods get real contracts).

### Out of scope
- The JSON wire format (`*.ir.json`) — UNCHANGED (serialization layer converts sums → dicts). The IR-conformance goldens stay byte-identical.
- The formal-semantics `Stmt` inductive — already a sum type; this refactor aligns the PyCSL IR with it (LINK 1), but doesn't change the formal model.
- The 6 lowering extensions already landed — they remain (they're independently valuable and some are still needed: e.g. newline-escaping for the emitted WhyML strings, string-keyed dicts for the emitter's own config).

### NOT changed
- The `#@` annotation syntax, the parser, the proof infrastructure — none of this touches the refactor.

---

## 6. The migration: dual-representation (the safe path)

A full `Dict[str, Any]` → typed-sum rewrite in one pass is high-risk (it touches Module5 emission, Module6 consumption, and every `_handle_*` method). Use the **dual-representation** path:

### Phase A — Add the typed sums alongside the dicts (additive)
1. Define `StmtIR`/`ExprIR`/`ContractExprIR` sum classes in `ir_schema.py` with a `from_dict`/`to_dict` converter (the dicts stay the canonical wire format).
2. Module5 keeps emitting `Dict[str, Any]` (unchanged) — but ALSO constructs the typed sums (or a post-pass converts dicts → sums).
3. Nothing consumes the sums yet. Standing gate: byte-identical (the sums are additive; the JSON output is unchanged).

### Phase B — Migrate Module6 consumers to the sums (one `_handle_*` at a time)
1. Module6's `_stmts_to_whyml` converts each `Dict[str, Any]` stmt to a `StmtIR` sum at entry (one `from_dict` call), then dispatches on the typed sum.
2. Migrate each `_handle_*` method to take a `StmtIR` subclass. One at a time, with the standing gate after each.
3. The dispatch table (`_STMT_HANDLERS`) becomes a typed `match`.
4. Standing gate: the corpus still proves identically (the emitted WhyML is byte-identical — the typed sum is an in-memory representation change, not a lowering change).

### Phase C — Re-annotate the emitter body-faithful (the payoff)
1. With the 12 `_handle_*` methods now consuming typed `StmtIR` fields, their bodies are typed field accesses (not `Any`-typed dict lookups).
2. Add the `StmtIR`/`ExprIR` WhyML variant declarations to the emitter's self-annotate model.
3. Strip `\trusted` from the 12 methods; give each a real contract (`ensures \result == <the WhyML string>` or `assigns \nothing` + a result postcondition).
4. The ones that still can't prove (due to self-mutation, sibling trusted calls) stay `\trusted` with a note — but the dict/`Any` blocker is gone.

---

## 7. The expected outcome

After Phase C, the 12 `_handle_*` methods fall into three buckets:

| Bucket | Methods | Why |
|---|---|---|
| **Body-faithful** (the leaf emitters + the simple compositional ones) | `_handle_pass_stmt`, `_handle_break_stmt`, `_handle_continue_stmt` (if extracted), `_handle_assign_stmt` (the fixed-string cases), `_handle_return_stmt` | Typed field access + fixed WhyML shape → real `ensures` |
| **Body-faithful with effort** (compositional) | `_handle_if_stmt`, `_handle_seq_stmt`, `_handle_while_stmt`, `_handle_for_stmt` | Typed fields + WhyML composition; may need string-concat postconditions |
| **Still `\trusted`** (self-mutation / sibling trusted calls) | `_handle_try_stmt`, `_handle_match_stmt`, `_handle_array_slice_set_stmt` (the complex lowering), `_handle_critical_section_stmt` | Even typed, these mutate `self` or call trusted siblings — a separate modeling effort |

The refactor closes the **`Any`-typed dict blocker** for all 12. The residual blockers (self-mutation, sibling calls) are honest and scoped — not architectural.

---

## 8. Sequencing & effort

| Phase | Effort | Risk | Gate |
|---|---|---|---|
| A — add typed sums (additive) | Medium — define ~30 sum classes + from_dict/to_dict | Low (additive; JSON unchanged) | byte-identical corpus |
| B — migrate Module6 consumers (one method at a time) | High — 12 `_handle_*` methods + the dispatch | Medium (per-method gate) | byte-identical after each |
| C — re-annotate body-faithful | Medium — strip `\trusted`, add real contracts | Low (the typed schema makes the bodies provable) | self-annotate proves |

**Critical path:** A → B → C. Phase B is the long pole (12 methods, each gated by the corpus). The refactor is mechanical (dict → typed field access) but large — the safest execution is per-method in Phase B, with the standing gate after each.

---

## 9. What this closes (and doesn't)

### Closes
- **LINK 3** for the leaf + compositional `_handle_*` methods — the bridge from the implementation to `module6_encodes_mlw` becomes provable per-method (the body-faithful contract IS the per-method statement of the axiom).
- **LINK 1 alignment** — the PyCSL IR `StmtIR` sum aligns constructor-by-constructor with the formal-semantics `Stmt` inductive, making the AST↔IR correspondence (the Sub-α theorem) constructor-complete.

### Does NOT close
- The residual `\trusted` methods in bucket 3 (self-mutation / sibling calls) — these need a transpiler-state record model (modeling `self._add_abstract_op` etc. as `assigns`), a separate effort.
- The end-to-end `module6_encodes_mlw` theorem — still needs the body-faithful contracts to compose into the per-method axiom. The refactor makes this PROVABLE; proving it is the post-refactor work.

The refactor converts the 12-method blocker from "architectural (can't type-check `Any`)" to "mechanical (typed field access, prove per-method)" — the necessary precondition for LINK 3 to close.

---

## 10. Actual outcome (Phases A–C executed 2026-06-28)

### Phase A — COMPLETE
- `src/pycsl/ir_schema.py` — 110 typed sum classes defined: 24 `StmtIR` constructors, 84 `ExprIR` constructors, `ContractExprIR` (alias for `ExprIR`), 1 `OpaqueStmt`/`OpaqueExpr` fallback each.
- `from_dict`/`to_dict` converters; round-trip test (`tests/test_ir_schema_roundtrip.py`) — 42 passed, walks 1127 IR nodes across all corpus goldens, asserts `to_dict(from_dict(d)) == d`.
- ADDITIVE: Module5/Module6 unchanged. Standing gate byte-identical.
- Commit: `4c386eed feat(ir-schema): add typed StmtIR/ExprIR sum classes (Phase A)`.

### Phase B — COMPLETE
- `src/pycsl/module6_whyml/statements.py` — entry-point `_stmts_to_whyml` rewritten to convert each wire dict to a `StmtIR` sum via `stmt_from_dict` and dispatch via `isinstance`; the `_STMT_HANDLERS` dispatch table REMOVED (replaced by typed dispatch).
- All 19 handlers migrated (12 table-driven + 7 inline): GhostAssign, GhostArraySet, Assign, TupleUnpack, AugAssign, FieldAssign, FieldAugAssign, ArraySet, ArraySliceSet, While, Return, If, For, Expr, Try, Match, CriticalSection + Label, Continue, Raise, ProofAssert, Assert, Pass, Break.
- `src/pycsl/module6_whyml/stmt_control_flow.py` — the compositional handlers (`_handle_while_stmt`, `_handle_for_stmt`, `_handle_if_stmt`, `_handle_try_stmt`, `_handle_match_stmt`, `_handle_return_stmt`) migrated to typed sums.
- Fixed a Phase-A schema bug: `LambdaExpr.body` was `List[StmtIR]` but Module5 emits a single expression → corrected to `ExprIR`.
- **624-file byte-diff sweep: 0 differences.** The typed sum is a pure in-memory representation change; the emitted WhyML is byte-identical.
- Commit: `ebdf0cd1 refactor(ir-schema): migrate Module6 statement handlers to typed StmtIR sums (Phase B)`.

### Phase C — PARTIAL (honest)
- `src/self-annotate/src/module6_whyml/statements.py` — re-annotated. The code matches the Phase-B-migrated real source exactly. Added `#@ datatype expr_ir = …` and `#@ datatype stmt_ir = …` (module-level) mirroring the Phase-A sums.
- **Body-faithful: 2 methods** (`_materialize_bridge`, `_materialize_str_bridge`) — trivial bridge methods with `requires True; ensures True; assigns \nothing`.
- **Still `\trusted`: 24 methods** (the 12 `_handle_*` + 12 internal helpers). Four honest, scoped blockers (documented at `statements.py:47`):
  - **B1 — Opaque `ir_schema` import (DOMINANT):** pycsl skips `from ir_schema import AssignStmt, stmt_from_dict, …` in single-file isolation ("external module, no local source found"). So `stmt: AssignStmt` is opaque and `stmt.target` is an Any-typed getattr — **the Phase A+B typed-schema payoff does NOT transfer to single-file isolation** without cross-file type resolution.
  - **B2 — f-string hashing:** the `_handle_*` bodies build the emitted WhyML string with f-strings (`f"{indent}let {safe_target} := {val}"`). pycsl lowers f-string literal segments to hashed INTs → `str_concat` receives an int where a string is expected → WhyML type error. A real `ensures \result == "…" ^ body_code ^ "…"` is expressible in the contract grammar, but the BODY can't verify against it.
  - **B3 — Trusted sibling returns:** `_handle_*` bodies call `self._expr_to_whyml` / `self._stmts_to_whyml` (themselves `\trusted`, `ensures True`); the emitted string depends on those unmodeled return values.
  - **B4 — Self-mutation:** many bodies mutate transpiler state (`self._dict_locals.add`, `self._add_abstract_op`, …) with no transpiler-state record model, so the frame (`assigns`) can't be stated soundly.
- Commit: `2106f891 feat(self-annotate): re-annotate module6 statements.py body-faithful (Phase C)`.

### Net assessment
The refactor SUCCEEDED in its stated goal — the **`Any`-typed dict blocker is closed in the real codebase** (Module6 now consumes typed `StmtIR` sums; 624-file byte-diff clean). LINK 1 alignment is achieved: the PyCSL IR `StmtIR` sum aligns constructor-by-constructor with the formal-semantics `Stmt` inductive.

But LINK 3 (the body-faithful bridge to the self-annotate copy) is **NOT yet closed**: the typed-schema payoff doesn't transfer to single-file isolation (B1), compounded by f-string hashing (B2). The next blocker to attack is **cross-file type resolution** (so `from ir_schema import AssignStmt` resolves in self-annotate), then **f-string literal-segment lowering** (so `f"{indent}..."` builds a string, not a hashed int).

The 4 blockers are now all MECHANICAL, not architectural — the `Any`-typed wall is gone; these are lowering-extension gaps.
