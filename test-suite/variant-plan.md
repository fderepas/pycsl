# variant-plan.md — Adding Function Variants and Termination Proofs to PyCSL

## Current State

**Loop variants: ✅ Fully supported.**
`#@ loop variant <expr>` is parsed, woven, emitted to IR, and transpiled to
WhyML `variant { ... }` inside `while`/`for` loops. Working end-to-end.

**Function variants / termination: ❌ Not supported.**
PyCSL has no annotation for proving that a recursive function terminates.
Every function is emitted as `let f ...` (non-recursive). There is:

- No `#@ \variant <expr>` annotation at function level
- No detection of recursive calls in the Python AST
- No `let rec f ... variant { ... }` emission in WhyML
- No `diverges` clause for intentionally non-terminating functions
- No structural variant support (e.g., termination on algebraic data types)

When a user writes a recursive function today, PyCSL either:
1. Silently emits `let f ...` (no recursion in WhyML → call to `f` inside body
   is an *unresolved name*, causing a Why3 error), or
2. Works only if the recursion was manually unrolled into a loop.

## Why This Matters

- Recursive algorithms (factorial, Fibonacci, GCD, mergesort, tree traversals)
  are common. Users expect to annotate and verify them.
- Without `let rec` + `variant`, Why3 rejects any self-referencing function.
- The `diverges` clause is needed for infinite-loop servers, REPLs, etc.
- ACSL/Frama-C, JML, and Dafny all have function-level `decreases` /
  `variant` clauses. PyCSL should too.

## Proposed Annotations

### 1. Function variant — integer termination measure

```python
#@ requires n >= 0
#@ ensures \result >= 1
#@ \variant n
def factorial(n: int) -> int:
    if n == 0:
        return 1
    return n * factorial(n - 1)
```

Transpiles to:
```whyml
let rec factorial (n: int) : int
  requires { n >= 0 }
  ensures  { result >= 1 }
  variant  { n }
=
  if (n = 0) then
    1
  else
    (n * factorial (n - 1))
```

### 2. Structural variant — termination on algebraic structures

WhyML supports `variant { t } with ordering` where `ordering` is a
well-founded relation (e.g., `structural` for algebraic types, or a
user-defined order). PyCSL exposes this via an optional second argument:

```python
#@ \variant (t, subterm)
def tree_size(t) -> int:
    ...
```

Transpiles to:
```whyml
let rec tree_size (t: tree) : int
  variant { t } with subterm
=
  ...
```

The syntax is `\variant <expr>` (integer, default) or
`\variant (<expr>, <ordering>)` (structural, with named well-founded relation).

### 3. Diverges (intentionally non-terminating)

```python
#@ \diverges
def event_loop() -> None:
    while True:
        handle_event()
```

Transpiles to:
```whyml
let event_loop () : unit
  diverges
=
  ...
```

## Implementation Plan

### Module 2 — Parser (`Module2_Parser.py`)

**Add two new CSL node types:**

```python
class FunctionVariant(CSLNode):
    """#@ \\variant <expr>  or  #@ \\variant (<expr>, <ordering>)"""
    def __init__(self, expr, ordering=None):
        self.expr = expr
        self.ordering = ordering   # None → integer, str → named relation

class Diverges(CSLNode):
    """#@ \\diverges"""
    pass
```

**Extend the grammar:**

```
contract: requires | ensures | assigns
        | loop_invariant | loop_variant
        | class_invariant | label_decl
        | function_variant | diverges_decl

function_variant: VARIANT_KW expr                      -> function_variant
                | VARIANT_KW "(" expr "," NAME ")"     -> function_variant_structural
diverges_decl:    DIVERGES_KW

VARIANT_KW:  "\\variant"
DIVERGES_KW: "\\diverges"
```

The `\variant` backslash prefix follows the same convention as `\result`,
`\old`, `\forall`, etc. — it marks a PyCSL-specific keyword that cannot
collide with Python identifiers. No disambiguation rule is needed; `loop
variant` (two words, no backslash) remains the loop-level annotation.

**Effort:** ~20 lines.

---

### Module 1 — Ingestor (`Module1_Ingestor.py`)

No structural change needed. The ingestor already extracts all `#@` comments
and sends them to Module 2 for parsing. `FunctionVariant` and `Diverges` will
be returned by the parser and associated with `FunctionDef` nodes via the
existing line-number mechanism.

**Effort:** 0 lines (automatic).

---

### Module 3 — Weaver (`Module3_Weaver.py`)

**Attach new contract types to `FunctionDef` nodes:**

```python
def visit_FunctionDef(self, node):
    ...
    node.csl_function_variants = []
    node.csl_diverges = False
    for c in contracts:
        ...
        elif isinstance(c, FunctionVariant):
            node.csl_function_variants.append(c)
        elif isinstance(c, Diverges):
            node.csl_diverges = True
```

**Validation:** Error if both `\variant` and `\diverges` are present on the
same function (contradictory: one asserts termination, the other denies it).

**Effort:** ~15 lines.

---

### Module 4 — Semantic Analyzer (`Module4_SemanticAnalyzer.py`)

**Validate variables in function variant expressions:**

The variant expression must reference only the function's parameters (same
scope rules as `requires`/`ensures`).

```python
for fv in getattr(node, 'csl_function_variants', []):
    self._validate_expr(fv.expr, param_names, f"function variant for '{node.name}'")
```

**Effort:** ~5 lines.

---

### Module 5 — IR Emitter (`Module5_IREmitter.py`)

**Emit new IR fields for function declarations:**

```python
def visit_FunctionDef(self, node):
    ...
    func_ir["function_variants"] = self._csl_list_to_ir(
        getattr(node, 'csl_function_variants', []))
    func_ir["diverges"] = getattr(node, 'csl_diverges', False)
```

For structural variants, include the ordering name:
```json
{
  "name": "factorial",
  "function_variants": [
    {"expr": {"type": "Var", "name": "n"}, "ordering": null}
  ],
  "diverges": false,
  ...
}
```

A structural variant would have `"ordering": "subterm"` instead of `null`.

**Effort:** ~10 lines.

---

### Module 6 — WhyML Transpiler (`Module6_WhyMLTranspiler.py`)

This is the most substantial change.

#### 6a. Detect recursive calls

Add a helper that scans a function's body IR for calls to the function itself:

```python
def _is_recursive(self, name: str, stmts: list) -> bool:
    """Check if any statement contains a call to `name`."""
    for stmt in stmts:
        if self._expr_calls(name, stmt):
            return True
    return False
```

This determines whether to emit `let` vs `let rec`.

#### 6b. Emit `let rec` + `variant` / `diverges`

In the function emission block (~line 715):

```python
keyword = "let rec" if is_recursive or has_function_variant else "let"
out.append(f"  {keyword} {name} {args_str} : {return_type}")
...
for fv in func.get("function_variants", []):
    fv_str = self._expr_to_whyml(fv["expr"], spec_refs)
    ordering = fv.get("ordering")
    if ordering:
        out.append(f"    variant  {{ {fv_str} }} with {ordering}")
    else:
        out.append(f"    variant  {{ {fv_str} }}")
if func.get("diverges"):
    out.append(f"    diverges")
```

#### 6c. Emit recursive calls in body

Currently, function calls in the body are not emitted (PyCSL targets
single-function verification). Add handling for `Call` IR nodes where the
callee matches a known function name:

```python
elif s_type == "Call" and stmt.get("func") == current_function_name:
    args = " ".join(self._expr_to_whyml(a, local_refs) for a in stmt["args"])
    code = f"{indent}{stmt['func']} {args}"
```

Also handle recursive calls in expressions (the return value case):
```python
elif t == "Call":
    args = " ".join(self._expr_to_whyml(a, local_refs) for a in expr["args"])
    return f"({expr['func']} {args})"
```

**Effort:** ~40 lines.

---

### Module 5 — IR Emitter (addendum): Emit function calls in body

Currently Module 5 emits `ast.Call` nodes only for `range()` in for-loop
iterators and `min()`/`max()` builtins. Recursive calls like `factorial(n-1)`
are either ignored or cause an error.

**Add a `Call` statement/expression IR node:**

```python
# In expression handling:
elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
    return {
        "type": "Call",
        "func": node.func.id,
        "args": [self._expr_node(a) for a in node.args]
    }
```

This is needed for both recursive calls and (future) inter-procedural calls.

**Effort:** ~15 lines.

---

### Test Suite

#### New tests for `test-suite/corpus/pycsl-reference/`:

| # | Test | Description |
|---|------|-------------|
| 0049 | Recursive factorial | `#@ \variant n`, `let rec` |
| 0050 | Recursive GCD | `#@ \variant b` (Euclidean) |
| 0051 | Recursive sum | `#@ \variant n`, accumulator pattern |
| 0052 | Diverges | `#@ \diverges`, infinite loop |
| 0053 | Multi-argument variant | `#@ \variant a + b` |
| 0054 | Structural variant | `#@ \variant (t, subterm)` |

#### Update traceability:

- Add rows to `test-suite/annotations.md` §2.1 for `\variant` and `\diverges`
- Add corresponding rows to `test-suite/traceability-pycsl.md`

---

## Deferred Features

1. **Mutual recursion:** WhyML supports `let rec f ... with g ...` for mutually
   recursive functions. PyCSL currently processes functions independently.
   Supporting mutual recursion requires grouping co-recursive functions and
   emitting them in a single `let rec ... with ...` block.
   **Status:** Deferred to a later phase; will be documented as unsupported.

2. **Recursive calls in contracts:** Allowing expressions like
   `ensures \result == n * factorial(n-1)` requires the function to be
   available in the logic scope (WhyML `function` instead of `let`).
   **Status:** Deferred; only imperative recursion for now.

## Design Decisions

1. **`\variant` keyword (not bare `variant`):** The backslash prefix follows
   PyCSL's convention for built-in keywords (`\result`, `\old`, `\forall`,
   `\exists`, `\length`, etc.). This eliminates any ambiguity with user
   variables named `variant` and is visually consistent with the rest of the
   annotation language.

2. **Call graph for `let rec` detection:** If the user writes `#@ \variant n`
   but the function is not actually recursive, we still emit `let rec` — it is
   harmless for non-recursive functions and `\variant` is an explicit opt-in.
   Auto-detection of recursion (without `\variant`) should also emit `let rec`
   with a warning about a missing variant.

## Summary

| Module | Change Size | Description |
|--------|-------------|-------------|
| Module2_Parser | ~20 lines | `FunctionVariant` / `Diverges` nodes + grammar (`\variant`, `\diverges`) |
| Module3_Weaver | ~15 lines | Attach to `FunctionDef`, validate no `\variant` + `\diverges` conflict |
| Module4_SemanticAnalyzer | ~5 lines | Scope-check variant expressions |
| Module5_IREmitter | ~25 lines | Emit `function_variants` (with ordering), `diverges`, `Call` nodes |
| Module6_WhyMLTranspiler | ~45 lines | `let rec`, `variant {} [with ordering]`, `diverges`, recursive calls |
| Test suite | ~6 files | New pycsl-reference tests (integer + structural variant) + traceability |
| **Total** | **~115 lines** | |
