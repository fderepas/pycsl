# Module4\_SemanticAnalyzer.py — Refactoring Plan

**File:** `src/pycsl/Module4_SemanticAnalyzer.py` (398 lines, 17 methods)

---

## 1  Diagnostic Summary

### 1.1  God Methods

No method exceeds 100 lines.  One is close:

| Method | Lines | Location | Notes |
|--------|------:|----------|-------|
| `visit_FunctionDef` | 90 | L291–381 | 6 numbered phases + concurrency check.  Borderline god method — mixes scope building, contract validation, assigns-region checks, subscript checks, and concurrency checks. |
| `extract_variables` (module fn) | 38 | L17–55 | 13-branch isinstance chain over CSL nodes |
| `_check_protected_in_stmt` | 38 | L159–197 | 8-branch isinstance chain over `ast.*` nodes |
| `visit_ClassDef` | 35 | L254–289 | Field collection + class-invariant validation |

### 1.2  Duplicated CSL Traversals

Three functions independently walk the `CSLNode` tree with nearly identical isinstance chains:

| Function | Purpose | Branches |
|----------|---------|-------:|
| `extract_variables` | Collect referenced variable names | 13 |
| `contains_result` | Check if `\result` appears anywhere | 8 |
| `_validate_predicate_bases` | Check `\valid`/`\separated` bases | 7 |

All three share the same structural recursion pattern (BinOp → recurse left/right; SingleExprNode → recurse expr; ContractWrapper → recurse expr; QuantifierNode → recurse body; etc.).  This is a textbook case for a **generic CSL walker** with a pluggable visitor callback.

### 1.3  isinstance Count

- Total: **55** `isinstance` calls
- `elif isinstance`: **26** branches
- After refactoring: target ≤ 25

### 1.4  Missing Annotations

- `_validate_predicate_bases` — missing return type annotation (should be `-> None`)
- File lacks `from __future__ import annotations`

### 1.5  Other Findings

| Check | Result |
|-------|--------|
| Regex usage | 0 — clean |
| `sys.exit` in library code | 0 — clean |
| `except ImportError` fallback | 0 — clean |
| Hardcoded IPs/URLs | 0 — clean |
| Module-level globals | State is in `__init__` — clean |

---

## 2  Refactoring Steps

### Step 1 — Extract a generic CSL walker (deduplication)

**Problem:**  `extract_variables`, `contains_result`, and `_validate_predicate_bases` each contain their own isinstance chain for the same ~8 structural CSL node types (BinOp, SingleExprNode, ContractWrapper, QuantifierNode, etc.).  Adding a new CSL node type requires updating all three.

**Solution:** Create a `_walk_csl(node)` generator (or `_iter_csl_children(node)` helper) that yields the direct child CSL nodes for any given node.  Then each function collapses to:
- `extract_variables`: accumulate `Var.name` while recursing children
- `contains_result`: check `Result` or `SubscriptAccess(\result)`, then recurse
- `_validate_predicate_bases`: check `Valid`/`Separated`, then recurse

```python
def _iter_csl_children(node: CSLNode) -> List[CSLNode]:
    """Yield direct CSL sub-expressions of a node."""
    if isinstance(node, BinOp):
        return [node.left, node.right]
    if isinstance(node, SingleExprNode):   # UnaryOp, Old
        return [node.expr]
    if isinstance(node, ContractWrapper):   # Requires, Ensures, ...
        return [node.expr]
    if isinstance(node, FunctionVariant):
        return [node.expr]
    if isinstance(node, QuantifierNode):    # Forall, Exists
        return [node.body]
    if isinstance(node, Assigns):
        return list(node.targets)
    if isinstance(node, SubscriptAccess):
        return [node.index]
    if isinstance(node, AssignsRegion):
        return [node.low, node.high]
    if isinstance(node, Valid):
        return [node.length]
    if isinstance(node, Separated):
        return [node.length1, node.length2]
    return []
```

Then `extract_variables` becomes:

```python
def extract_variables(node: CSLNode) -> Set[str]:
    if isinstance(node, Var):
        return {node.name}
    if isinstance(node, FieldAccess):
        return set()
    if isinstance(node, ArrayLength):
        return {node.var}
    if isinstance(node, SubscriptAccess):
        base = set() if node.array == "\\result" else {node.array}
        return base | extract_variables(node.index)
    if isinstance(node, AssignsRegion):
        return {node.base} | extract_variables(node.low) | extract_variables(node.high)
    if isinstance(node, Valid):
        return {node.base} | extract_variables(node.length)
    if isinstance(node, Separated):
        return ({node.base1} | extract_variables(node.length1) |
                {node.base2} | extract_variables(node.length2))
    if isinstance(node, QuantifierNode):
        return extract_variables(node.body) - {node.var}
    # Generic structural recursion
    result: Set[str] = set()
    for child in _iter_csl_children(node):
        result |= extract_variables(child)
    return result
```

And `contains_result` becomes:

```python
def contains_result(node: CSLNode) -> bool:
    if isinstance(node, Result):
        return True
    if isinstance(node, SubscriptAccess) and node.array == "\\result":
        return True
    return any(contains_result(c) for c in _iter_csl_children(node))
```

And `_validate_predicate_bases` becomes:

```python
def _validate_predicate_bases(self, node: CSLNode, context_name: str) -> None:
    if isinstance(node, Valid):
        # ... existing check ...
        pass
    elif isinstance(node, Separated):
        # ... existing check ...
        pass
    for child in _iter_csl_children(node):
        self._validate_predicate_bases(child, context_name)
```

**Effect:** eliminates ~20 duplicate isinstance branches; adding a new CSL node type only requires updating `_iter_csl_children`.

**Effort:** Quick win (≤ 2h)

---

### Step 2 — Split `visit_FunctionDef` into phases

**Problem:** `visit_FunctionDef` (90 lines) has 6 numbered phases plus a concurrency check, all in one method.

**Solution:** Extract each phase as a private helper:

| Helper | Phase | Purpose |
|--------|-------|---------|
| `_build_function_scope(node)` | 1–3 | Populate `current_scope` from args, locals, ghost variables |
| `_validate_function_contracts(node)` | 4 | Validate requires, ensures, assigns, function variants |
| `_validate_assigns_regions(node)` | 4b | Check assigns regions reference list-typed params |
| `_validate_subscript_assignments(node)` | 5 | Check `arr[i] = v` targets are list-typed |

The orchestrator `visit_FunctionDef` becomes ~20 lines:

```python
def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
    saved_scope = self.current_scope
    saved_function_name = self.current_function_name
    self.current_function_name = f"function '{node.name}'"
    self.current_scope = {}

    self._build_function_scope(node)
    self._validate_function_contracts(node)
    self._validate_assigns_regions(node)
    self._validate_subscript_assignments(node)

    node.csl_symbol_table = self.current_scope.copy()

    if self._shared_vars:
        self._check_protected_in_stmts(node.body, set(), node.name)

    self.generic_visit(node)
    self.current_scope = saved_scope
    self.current_function_name = saved_function_name
```

**Effort:** Medium (≤ 1h)

---

### Step 3 — Dispatch table for `_check_protected_in_stmt`

**Problem:** `_check_protected_in_stmt` (38 lines) has an 8-branch isinstance chain over `ast.With`, `ast.If`, `ast.While`, `ast.For`, `ast.Assign`, `ast.AugAssign`, `ast.Return`, `ast.Expr`.

**Solution:** Replace with a dispatch table:

```python
_PROTECTED_HANDLERS: Dict[type, str] = {
    ast.With:       "_protected_with",
    ast.If:         "_protected_if",
    ast.While:      "_protected_loop",
    ast.For:        "_protected_loop",
    ast.Assign:     "_protected_assign",
    ast.AugAssign:  "_protected_aug_assign",
    ast.Return:     "_protected_return",
    ast.Expr:       "_protected_expr",
}
```

Each handler is a 3–8 line method.  The dispatcher becomes:

```python
def _check_protected_in_stmt(self, node: ast.AST, held: Set[str], func_name: str) -> None:
    handler_name = self._PROTECTED_HANDLERS.get(type(node))
    if handler_name:
        getattr(self, handler_name)(node, held, func_name)
```

**Effect:** eliminates 8 isinstance/elif branches; O(1) dispatch.

**Effort:** Quick win (≤ 1h)

---

### Step 4 — Add missing type annotations

1. Add `from __future__ import annotations` as first line
2. Fix `_validate_predicate_bases(self, node: CSLNode, context_name: str) -> None:`
3. Add `Set` import if not already present
4. Annotate `_check_protected_in_stmt` and helpers with explicit `-> None`

**Effort:** Quick win (≤ 30 min)

---

### Step 5 — Extract `visit_ClassDef` helpers

**Problem:** `visit_ClassDef` (35 lines) mixes field-collection and invariant-validation.

**Solution:** Extract `_collect_class_field_types(node) -> Dict[str, str]` (reusable pattern matching Module5's `_collect_class_fields`).

```python
def _collect_class_field_types(self, node: ast.ClassDef) -> Dict[str, str]:
    """Scan __init__ for self.x assignments and return {field_name: type_name}."""
    fields: Dict[str, str] = {}
    for child in node.body:
        if isinstance(child, ast.FunctionDef) and child.name == '__init__':
            for stmt in ast.walk(child):
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if (isinstance(target, ast.Attribute) and
                                isinstance(target.value, ast.Name) and
                                target.value.id == 'self'):
                            fields[target.attr] = 'Any'
                elif isinstance(stmt, ast.AnnAssign):
                    if (isinstance(stmt.target, ast.Attribute) and
                            isinstance(stmt.target.value, ast.Name) and
                            stmt.target.value.id == 'self'):
                        fields[stmt.target.attr] = (
                            self._get_type_name(stmt.annotation)
                            if stmt.annotation else 'Any'
                        )
    return fields
```

Then `visit_ClassDef` simplifies to:

```python
def visit_ClassDef(self, node: ast.ClassDef) -> Any:
    self._class_fields = self._collect_class_field_types(node)
    for inv in getattr(node, 'csl_class_invariants', []):
        context = f"class invariant for '{node.name}'"
        referenced = extract_variables(inv.expr)
        for var_name in referenced:
            if var_name not in self._class_fields:
                raise PyCSLSemanticError(...)
    self.generic_visit(node)
    self._class_fields = {}
```

**Effort:** Quick win (≤ 30 min)

---

## 3  Execution Order

| Order | Step | Depends On | Verification |
|------:|------|-----------|--------------|
| 0 | Baseline test run | — | Record pass count |
| 1 | Step 1: CSL walker | — | `py_compile` + smoke + test suite |
| 2 | Step 2: Split `visit_FunctionDef` | — | `py_compile` + smoke + test suite |
| 3 | Step 3: Dispatch table for `_check_protected_in_stmt` | — | `py_compile` + smoke + test suite |
| 4 | Step 4: Type annotations | Steps 1–3 | `py_compile` |
| 5 | Step 5: Extract `visit_ClassDef` helper | — | `py_compile` + smoke + test suite |
| 6 | Final test run | Steps 1–5 | Full test suite ≥ baseline |

Steps 1, 2, 3, 5 are independent and can be done in any order.
Step 4 (type annotations) should come last to avoid merge conflicts with other steps.

---

## 4  Verification Protocol

1. **Baseline:** `./bin/run-reference-tests.sh` — record pass count (currently 784/784)
2. **After each step:**
   - `python3 -m py_compile src/pycsl/Module4_SemanticAnalyzer.py`
   - Quick smoke test: annotate a file with contracts, class invariants, and concurrency annotations
   - Run `./bin/run-reference-tests.sh`
3. **Final:** full test suite must be ≥ baseline

---

## 5  Non-Changes (out of scope)

These are explicitly **not** being refactored:

- **Error hierarchy** — Module4 already uses `PyCSLSemanticError` consistently; no `sys.exit` in library code
- **Logging** — no logging in Module4 (it's a pure analysis pass that raises on error)
- **Regex** — no regex in Module4
- **Config** — no hardcoded values
- **Concurrency helpers** — `_check_protected_in_stmt` dispatch table (Step 3) is the only touch; the lock-order logic is well-structured

---

## 6  Expected Metrics

| Metric | Before | Target |
|--------|-------:|-------:|
| Total lines | 398 | ~420 (slight growth from extracted helpers) |
| God methods (>100 lines) | 0 | 0 |
| Largest method | 90 (`visit_FunctionDef`) | ≤ 25 |
| `isinstance` count | 55 | ≤ 25 |
| `elif isinstance` | 26 | ≤ 8 |
| Methods | 17 | ~28 |
| Missing return types | 1 | 0 |
| Duplicated traversal patterns | 3 | 0 (unified via `_iter_csl_children`) |
| Test pass rate | 784/784 | ≥ 784/784 |

---

## 7  Risks

| Risk | Mitigation |
|------|------------|
| `_iter_csl_children` misses a node type → silent data loss in `extract_variables` | Compare output before/after on every reference test (functional equivalence) |
| Dispatch table for `_check_protected_in_stmt` misses `ast` subclass inheritance | `ast.With`, `ast.If`, etc. are concrete types — no subclass issue (unlike `ContractWrapper` in Module5) |
| `visit_FunctionDef` split breaks save/restore of `current_scope` | Keep save/restore in the orchestrator method, not in helpers |
