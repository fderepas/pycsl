# Level 4+: Mutable Arrays, Quantifiers, For-Loops & Built-ins

## Context

All prior levels (1–3) are complete:
- **Level 1** — basic function contracts (`requires`, `ensures`, `assigns`)
- **Level 2** — class record types (methods, `self.field`, `\old(self.field)`)
- **Level 3** — class invariants (`#@ class invariant`, `by` witness)

This plan adds four tightly-coupled features that share a common foundation:
switching from Why3's immutable `seq.Seq` to mutable `array.Array`.

### Why3 evidence (verified before planning)

```whyml
module Test
  use int.Int
  use ref.Ref
  use array.Array

  (* Read: a[i], length a *)
  (* Write: a[i] <- v      *)
  (* Quantifiers in specs: forall i. 0 <= i < n -> a[i] >= 0  → Valid *)

  let sum_arr (a: array int) (n: int) : int
    requires { n >= 0 /\ length a = n }
    requires { forall i. 0 <= i < n -> a[i] >= 0 }
    ensures  { result >= 0 }
  = ...   (* Alt-Ergo: Valid *)
end
```

Arrays support both read and write; `seq` was read-only. Switching is a clean
breaking change that simplifies the model.

---

## Feature 1 — Mutable Arrays (replace `seq.Seq` with `array.Array`)

### Design decision

Replace `seq int` with `array int` for all list parameters everywhere in the
pipeline. `array.Array` is a strict superset of `seq.Seq` for our use-case:

| Operation | `seq.Seq` (old) | `array.Array` (new) |
|-----------|-----------------|---------------------|
| Read element | `Seq.get a i` | `a[i]` |
| Write element | ❌ not supported | `a[i] <- v` |
| Length | `Seq.length a` | `length a` |
| Parameter type | `seq int` | `array int` |
| Import | `use seq.Seq` | `use array.Array` |

### Module 5 (`Module5_IREmitter.py`)

- `_py_expr_to_ir`: `ast.Subscript` already emits `{"type": "Subscript"}` — **no
  change needed** for reads.
- **New:** in `_py_stmts_to_ir`, handle `ast.Assign` where the target is
  `ast.Subscript`:
  ```python
  {"stmt": "ArraySet", "array": <ir_expr>, "index": <ir_expr>, "value": <ir_expr>}
  ```
- **New:** `ast.List` literal → `{"type": "ArrayLit", "elts": [...]}` (for
  `arr = [0, 1, 2]` style initialisation).
- Symbol-table type tag `"list"` is kept as-is; Module 6 maps it to `array int`.

### Module 6 (`Module6_WhyMLTranspiler.py`)

- **Header:** emit `use array.Array` (replaces `use seq.Seq`).  The trigger
  variable `needs_seq` is renamed `needs_array`; it fires when any function has a
  `list` parameter, uses a `For` IR node, or contains a `Subscript` expression.
- **Parameter type:** `"list"` symbol-table entry → `(param: array int)` (was
  `seq int`).
- **Expression `Subscript`:** emit `{value}[{index}]` (was `(Seq.get {value}
  {index})`).
- **New statement `ArraySet`:** emit `{array}[{index}] <- {val}`.
- **`len()` call:** emit `length {arg}` (was `(Seq.length {arg})`).
- **For-loop lowering:** update condition `!_idx < length {iter}` and element
  binding `let {target} = ref {iter}[!_idx] in` (was `Seq.length`/`Seq.get`).

### Module 4 (`Module4_SemanticAnalyzer.py`)

- When visiting `ast.Assign` with an `ast.Subscript` target, validate that the
  array variable is typed `list` in the current scope.  Raise
  `PyCSLSemanticError` for unknown or non-list variables.

### Test files (`tests/to_annotate/`)

| File | What it tests |
|------|---------------|
| `041-array-sum.py` | Sum of array elements (read-only, `\result >= 0`) |
| `042-array-fill.py` | Fill with zeros (`arr[i] = 0` mutation) |
| `043-array-search.py` | Linear search, returns index or -1 |
| `044-array-copy.py` | Copy src to dst element-by-element |
| `045-array-max.py` | Find maximum element |

---

## Feature 2 — Quantifiers in Contracts (`\forall`, `\exists`)

### Contract syntax (new)

```
#@ requires \forall i; 0 <= i < n ==> arr[i] > 0
#@ ensures  \exists i; 0 <= i < n and \result == arr[i]
```

The semicolon separates the bound variable from the expression.  `==>` is used
for `forall` (material implication) and `and` for `exists` (conjunction).

### `\length(arr)` atom (also new)

General function calls remain **banned** in contracts.  Array length is the one
exception, exposed via a dedicated syntax:

```
#@ requires \length(arr) > 0
#@ loop invariant i < \length(arr)
```

This keeps the grammar unambiguous and avoids a general function-call parser.

### Module 2 (`Module2_Parser.py`)

New dataclasses:
```python
@dataclass
class Forall(CSLNode):
    var: str
    domain: CSLNode   # the "0 <= i < n" part
    body: CSLNode     # the "arr[i] > 0" part

@dataclass
class Exists(CSLNode):
    var: str
    domain: CSLNode
    body: CSLNode

@dataclass
class ArrayLength(CSLNode):
    var: str          # array variable name
```

New Lark grammar rules (added to `?atom`):
```lark
| "\\forall" CNAME ";" expr "==>" expr  -> forall_expr
| "\\exists" CNAME ";" expr "and" expr  -> exists_expr
| "\\length" "(" CNAME ")"              -> array_length
```

Transformer methods: `forall_expr`, `exists_expr`, `array_length`.

### Module 4 (`Module4_SemanticAnalyzer.py`)

When validating a `Forall` or `Exists` node:
1. Push the bound variable (`node.var`) into a temporary child scope with type
   `int`.
2. Validate `node.domain` and `node.body` in that scope.
3. Pop the bound variable after validation.

`ArrayLength` is validated by checking that `node.var` is a `list`-typed
variable in the current scope.

### Module 5 (`Module5_IREmitter.py`)

In `_csl_to_ir`:
```python
elif isinstance(node, Forall):
    return {"type": "Forall", "var": node.var,
            "domain": self._csl_to_ir(node.domain),
            "body":   self._csl_to_ir(node.body)}
elif isinstance(node, Exists):
    return {"type": "Exists", "var": node.var,
            "domain": self._csl_to_ir(node.domain),
            "body":   self._csl_to_ir(node.body)}
elif isinstance(node, ArrayLength):
    return {"type": "ArrayLen", "var": node.var}
```

### Module 6 (`Module6_WhyMLTranspiler.py`)

In `_expr_to_whyml`:
```python
elif t == "Forall":
    var    = expr["var"]
    domain = self._expr_to_whyml(expr["domain"], local_refs)
    body   = self._expr_to_whyml(expr["body"],   local_refs)
    return f"forall {var}. ({domain}) -> ({body})"

elif t == "Exists":
    var    = expr["var"]
    domain = self._expr_to_whyml(expr["domain"], local_refs)
    body   = self._expr_to_whyml(expr["body"],   local_refs)
    return f"exists {var}. ({domain}) /\\ ({body})"

elif t == "ArrayLen":
    return f"length {expr['var']}"
```

---

## Feature 3 — For-Loop Desugaring (validate & complete)

The current `_process_for` (Module 5) and its Module 6 counterpart already
desugar `for item in arr:` into a while loop.  After Feature 1, `Seq.get` /
`Seq.length` calls become `a[i]` / `length a` automatically.

**Action:** after Feature 1 lands, run all existing for-loop tests to verify
no regression.  If the `_idx` ref is not yet in scope for loop invariants, fix
the emission order in `_stmts_to_whyml` for `For` nodes.

No new test files needed — the Feature 1 tests (`041`–`045`) exercise for-style
iteration patterns.

---

## Feature 4 — Built-in Functions (`len`, `min`, `max`)

### `len(a)`
Covered automatically by Feature 1 (`length a`).

### `min(a, b)` and `max(a, b)`

Why3 provides these in `int.MinMax`:
```whyml
use int.MinMax
(* Int.min a b, Int.max a b *)
```

**Module 6 changes:**
- New helper `_uses_minmax(functions) -> bool` — scans all bodies for a `Call`
  node with `func == "min"` or `func == "max"`.
- Header: conditionally emit `use int.MinMax` when `_uses_minmax` is true.
- In `_expr_to_whyml` `Call` handler:
  ```python
  elif func_name in ("min", "max") and len(args) == 2:
      fn = "Int.min" if func_name == "min" else "Int.max"
      return f"({fn} {args[0]} {args[1]})"
  ```

---

## Module-by-Module Summary

| Module | Feature 1 Arrays | Feature 2 Quantifiers | Feature 3 For | Feature 4 Built-ins |
|--------|------------------|-----------------------|---------------|---------------------|
| **M2 Parser** | — | `Forall`, `Exists`, `ArrayLength` nodes + grammar | — | — |
| **M3 Weaver** | — | — | — | — |
| **M4 Semantic** | Subscript-assign validation | Quantifier bound-var scoping, `ArrayLen` check | — | — |
| **M5 Emitter** | `ArraySet`, `ArrayLit` IR nodes | `Forall`/`Exists`/`ArrayLen` IR | Validate idx scope | `min`/`max` Call pass-through |
| **M6 Transpiler** | `array.Array`, `ArraySet`, `a[i]` syntax | `forall`/`exists` emission | `array.Array` for-loop | `Int.min/max`, `use int.MinMax` |

---

## Implementation Order (dependency-driven)

```
Feature 1 (arrays)          ← foundation; all others depend on array.Array
  └─ Feature 4 len          ← automatic from Feature 1
  └─ Feature 4 min/max      ← independent but trivial after F1
  └─ Feature 3 for-loop     ← validate after F1; likely needs no code change
Feature 2 (quantifiers)     ← independent of F1; needs \length which is part of F2
  └─ M2 grammar             ← first
  └─ M4 scoping             ← depends on M2
  └─ M5 IR nodes            ← depends on M2
  └─ M6 emission            ← depends on M5
Docs update                 ← last, after all features are proven Valid
```

---

## Skill Docs to Update (after implementation)

- `agents/skill-annotate.md` — array annotation patterns, `\forall`/`\exists`
  syntax, `\length()` in contracts, `min`/`max` usage
- `agents/skill-agents.md` — M2/M5/M6 section updates for new IR nodes and
  array.Array
- `agents/skill-module5.md` — `ArraySet`, `ArrayLit`, `Forall`, `Exists`,
  `ArrayLen` IR schemas
- `agents/skill-module6.md` — `array.Array` emission, quantifier WhyML output,
  `MinMax` conditional import

---

## Open Questions / Risks

1. **`fill_zeros` proof obligation** — Alt-Ergo returned `Unknown` for
   `ensures { forall i. 0 <= i < n -> a[i] = 0 }` after a fill loop.  This is
   a known limitation: the solver needs an explicit loop invariant
   `#@ loop invariant forall j; 0 <= j < i ==> arr[j] == 0`.  The
   `skill-annotate.md` must document this pattern.

2. **Quantifier variable naming conflicts** — the bound variable in `\forall i`
   must not shadow a function parameter named `i`.  Module 4 should warn on
   shadowing.

3. **`ArrayLit` initialisation** — `arr = [0] * n` cannot be directly lowered
   (requires a loop or `Array.make n 0`).  Module 5 may need to detect the
   `[0] * n` pattern specifically and emit a `MakeArray` IR node.

4. **`min`/`max` with list arguments** — `min(values)` (one argument, whole list)
   is not the same as `min(a, b)` (two integers).  Only the two-integer form is
   supported in this plan.  Document the restriction in `skill-annotate.md`.
