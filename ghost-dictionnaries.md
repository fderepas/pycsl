# Ghost Dictionary Variables — Implementation Plan

## Problem Statement

PyCSL ghost variables are currently **integer-only**. Ghost
dictionaries (finite maps from `int` to `int`) would let contracts
track key-value associations, element counts, visited sets,
histogram distributions, and inverse mappings — properties that
cannot be expressed with scalar, array, list, or tuple ghosts.

### Why dictionaries?

| Scenario | Why dict, not array? |
|----------|---------------------|
| Count occurrences of each value | Keys are arbitrary values, not 0..N-1 indices |
| Track which elements have been visited | Key set grows dynamically |
| Record inverse mapping (value → original index) | Keys come from array values, not positions |
| Histogram / frequency table | Sparse — most keys have count 0 |
| Set membership (ghost set) | Dictionary with value 1/0 = membership flag |

Ghost arrays require a known size at creation (`\make(n, 0)`).
Ghost dictionaries are **sparse** — only keys that are explicitly
set have non-default values.

### Target syntax

```python
#@ ghost freq : dict = \empty_map                     # empty map (all keys → 0)
#@ ghost freq = \map_set(freq, key, value)            # set key to value
#@ ghost freq = \map_set(freq, arr[i], \map_get(freq, arr[i]) + 1)  # increment
#@ ensures \map_get(freq, x) == count                 # read a key
#@ ensures \map_eq(freq1, freq2)                       # extensional equality
```

### Why3 target

```why3
use map.Map
use map.Const

let ghost freq = ref (Const.const 0 : map int int) in
ghost freq := Map.set !freq key value;
assert { Map.get !freq x = count };
```

Why3's `map.Map` provides a total function `int → int` with
`Map.get` and `Map.set`. `map.Const` provides `Const.const v`
which creates a map where every key maps to `v`. This is a perfect
match for ghost dictionaries.

---

## Current State (per module)

| Module | Dict support today | Ghost support today |
|--------|-------------------|-------------------|
| **Module2** (Parser) | No dict-specific contract syntax | Untyped, int only |
| **Module4** (Semantic) | `dict` type known for dict-typed params | Ghost: hard-coded `int` |
| **Module5** (IR Emitter) | `{"type":"DictLit", "keys":[...], "values":[...]}` | Ghost IR: no type field |
| **Module6** (Transpiler) | Dict literals → `val dict_new () : int` (abstract, uninterpreted); dict subscript → `subscript_get`/`subscript_set` (abstract); typed/store models use `map.Map` for the heap | Ghost: `ref int` only |

Key observations:
1. **Hoare model**: dicts are treated as opaque `int` values with
   abstract `subscript_get`/`subscript_set` operations — no
   reasoning about contents is possible.
2. **Typed/store models**: `map.Map` is already imported for the
   heap (`ref (map loc int)`), but not exposed to user contracts.
3. Ghost dictionaries would bring `map.Map` reasoning to the
   **hoare model** — currently the only way to reason about maps
   requires the typed/store model.

---

## Design Decisions

### D1. Why3 `map int int` — total function model

Ghost dictionaries are modeled as `map int int` (Why3's `map.Map`),
which is a **total function** from `int` to `int`. Every key has a
value; unset keys return the default (0 via `Const.const 0`).

This differs from Python's `dict` (partial, raises `KeyError`) but
is the standard verification approach (Dafny `map`, Frama-C `\lambda`).
For ghost purposes, totality is an advantage — no partiality VCs.

### D2. Storage model: ref-wrapped

Ghost dicts are ref-wrapped: `ref (map int int)`. Map values are
immutable (functional update via `Map.set` returns a new map):

```why3
let ghost m = ref (Const.const 0 : map int int) in
ghost m := Map.set !m key val;        (* functional update *)
assert { Map.get !m key = val }
```

### D3. Default value = 0

All ghost dicts are initialized with `Const.const 0` (every key maps
to 0). This matches Python's `defaultdict(int)` and `Counter()`
behavior. To use a different default:

```python
#@ ghost m : dict = \const_map(42)     # all keys → 42
```

### D4. Augmented assignments

- `+=` on dict ghost: **rejected** (ambiguous — add to what key?)
- `-=`, `*=`: **rejected**
- Only whole-map reassignment (`=`) is allowed

Element-level update uses `\map_set`:
```python
#@ ghost m = \map_set(m, key, \map_get(m, key) + 1)
```

---

## Implementation Plan

### Phase 1 — Grammar & AST (Module2)

**File: `src/pycsl/Module2_Parser.py`**

1. Extend `GhostAssignDecl` (shared with string/array/list/tuple):

```python
@dataclass
class GhostAssignDecl(CSLNode):
    target: str
    value: CSLNode
    op: str            # "=" only for dicts
    declared_type: str  # "int", "string", "array", "list",
                        # "tuple2"..."tuple4", "dict"
```

2. Add built-in expression nodes for map operations:

```lark
| "\\empty_map" -> empty_map_expr
| "\\const_map" "(" expr ")" -> const_map_expr
| "\\map_get" "(" expr "," expr ")" -> map_get_expr
| "\\map_set" "(" expr "," expr "," expr ")" -> map_set_expr
| "\\map_eq" "(" expr "," expr ")" -> map_eq_expr
| "\\map_dom" "(" expr "," expr ")" -> map_dom_expr
```

3. AST nodes:

```python
@dataclass
class EmptyMapExpr(CSLNode):
    """\\empty_map — the map where all keys → 0."""
    pass

@dataclass
class ConstMapExpr(CSLNode):
    """\\const_map(v) — the map where all keys → v."""
    default: CSLNode

@dataclass
class MapGetExpr(CSLNode):
    """\\map_get(m, k) — read key k from map m."""
    map_expr: CSLNode
    key: CSLNode

@dataclass
class MapSetExpr(CSLNode):
    """\\map_set(m, k, v) — functional update: return m with m[k] = v."""
    map_expr: CSLNode
    key: CSLNode
    value: CSLNode

@dataclass
class MapEqExpr(CSLNode):
    """\\map_eq(m1, m2) — extensional equality."""
    left: CSLNode
    right: CSLNode

@dataclass
class MapDomExpr(CSLNode):
    """\\map_dom(m, k) — true iff m[k] != default (k has been set)."""
    map_expr: CSLNode
    key: CSLNode
```

### Phase 2 — Weaver (Module3)

No change needed.

### Phase 3 — Semantic analysis (Module4)

**File: `src/pycsl/Module4_SemanticAnalyzer.py`**

1. Register ghost dicts in scope:

```python
ghost_type = getattr(ga, 'declared_type', 'int')
if ghost_type == "dict":
    self.current_scope[ga.target] = "ghost_dict"
```

2. Validation:
   - `+=`, `-=`, `*=` → error for dict ghosts
   - `\map_get`, `\map_set` → require dict-typed first arg
   - `\map_eq` → require both args dict-typed

### Phase 4 — IR emission (Module5)

**File: `src/pycsl/Module5_IREmitter.py`**

1. Carry type through IR (shared):

```python
ir_stmts.append({
    "stmt": "GhostAssign",
    "target": ga.target,
    "value": self._csl_to_ir(ga.value),
    "op": ga.op,
    "ghost_type": getattr(ga, 'declared_type', 'int'),
})
```

2. Add IR handlers for map operations:

```python
def _csl_empty_map(self, node) -> Dict[str, Any]:
    return {"type": "EmptyMap"}

def _csl_const_map(self, node) -> Dict[str, Any]:
    return {"type": "ConstMap",
            "default": self._csl_to_ir(node.default)}

def _csl_map_get(self, node) -> Dict[str, Any]:
    return {"type": "MapGet",
            "map": self._csl_to_ir(node.map_expr),
            "key": self._csl_to_ir(node.key)}

def _csl_map_set(self, node) -> Dict[str, Any]:
    return {"type": "MapSet",
            "map": self._csl_to_ir(node.map_expr),
            "key": self._csl_to_ir(node.key),
            "value": self._csl_to_ir(node.value)}

def _csl_map_eq(self, node) -> Dict[str, Any]:
    return {"type": "MapEq",
            "left": self._csl_to_ir(node.left),
            "right": self._csl_to_ir(node.right)}

def _csl_map_dom(self, node) -> Dict[str, Any]:
    return {"type": "MapDom",
            "map": self._csl_to_ir(node.map_expr),
            "key": self._csl_to_ir(node.key)}
```

### Phase 5 — WhyML transpiler (Module6)

**File: `src/pycsl/Module6_WhyMLTranspiler.py`**

#### 5a. Ghost dict declaration

In `_handle_ghost_assign_stmt`:

```python
if ghost_type == "dict":
    self._ghost_dict_vars.add(target)

    if target not in declared_refs:
        declared_refs.add(target)
        local_refs.add(target)
        rest_code = self._stmts_to_whyml(rest, ...)
        if not rest_code:
            rest_code = f"{indent}()"

        val_ir = stmt.get("value", {})
        if val_ir.get("type") == "EmptyMap":
            map_init = "(Const.const 0 : map int int)"
        elif val_ir.get("type") == "ConstMap":
            default = self._expr_to_whyml(val_ir["default"], local_refs)
            map_init = f"(Const.const {default} : map int int)"
        else:
            map_init = self._expr_to_whyml(stmt["value"], local_refs)

        return (f"{indent}let ghost {safe_target} = "
                f"ref {map_init} in\n{rest_code}")

    # Reassignment
    val_whyml = self._expr_to_whyml(stmt["value"], local_refs)
    code = f"{indent}ghost {safe_target} := {val_whyml}"
    if rest:
        code += ";\n" + self._stmts_to_whyml(rest, ...)
    return code
```

#### 5b. Map expression handlers

Add to `_expr_to_whyml` dispatch:

```python
if t == "EmptyMap":
    return "(Const.const 0 : map int int)"

if t == "ConstMap":
    default = self._expr_to_whyml(ir_expr["default"], local_refs, ...)
    return f"(Const.const {default} : map int int)"

if t == "MapGet":
    m = self._expr_to_whyml(ir_expr["map"], local_refs, ...)
    k = self._expr_to_whyml(ir_expr["key"], local_refs, ...)
    return f"(Map.get {m} {k})"

if t == "MapSet":
    m = self._expr_to_whyml(ir_expr["map"], local_refs, ...)
    k = self._expr_to_whyml(ir_expr["key"], local_refs, ...)
    v = self._expr_to_whyml(ir_expr["value"], local_refs, ...)
    return f"(Map.set {m} {k} {v})"

if t == "MapEq":
    left = self._expr_to_whyml(ir_expr["left"], local_refs, ...)
    right = self._expr_to_whyml(ir_expr["right"], local_refs, ...)
    return f"({left} = {right})"

if t == "MapDom":
    m = self._expr_to_whyml(ir_expr["map"], local_refs, ...)
    k = self._expr_to_whyml(ir_expr["key"], local_refs, ...)
    return f"(Map.get {m} {k} <> 0)"
```

#### 5c. Ghost dict variable tracking

1. Add `self._ghost_dict_vars: Set[str] = set()` to
   `_reset_function_state`.

2. Ghost dict vars use `!` dereference (ref-wrapped). The existing
   Var handler already emits `!` for variables in `local_refs`.

3. Exclude from parameter lists (same as other ghost vars).

#### 5d. Auto-import `map.Map` and `map.Const`

In hoare model, `map.Map` is NOT currently imported (only
typed/store models use it). Ghost dicts in hoare model require
adding it:

```python
# In _emit_preamble:
if needs.get("needs_map_ghost"):
    out.append("  use map.Map")
    out.append("  use map.Const")
```

This is independent of the typed/store model's map import (which
is for the heap, not for user-level ghost state).

Extend `_scan_preamble_needs`:

```python
needs_map_ghost = any(
    self._has_ghost_dict(body) for body in all_bodies
) or any(
    self._ir_uses_map_ops(body) for body in all_bodies
)
```

Where `_has_ghost_dict` scans for `GhostAssign` with
`ghost_type == "dict"`, and `_ir_uses_map_ops` scans for
`MapGet`, `MapSet`, `EmptyMap`, `ConstMap`, `MapEq`, `MapDom`
IR nodes.

---

### Phase 6 — Higher-level predicates

#### 6a. `\map_count(m, arr, lo, hi)` — counting predicate

Asserts that `m` is the frequency table of `arr[lo..hi)`:

```python
#@ ensures \map_count(freq, arr, 0, n)
```

Meaning: `∀ v. map_get(freq, v) == count of v in arr[0..n)`.

**Why3 logic function** (emitted in preamble when used):

```why3
let rec ghost function count_occ (a: array int) (lo hi v: int) : int
  requires { 0 <= lo }
  requires { hi <= length a }
  variant { hi - lo }
= if lo >= hi then 0
  else (if a[lo] = v then 1 else 0) + count_occ a (lo + 1) hi v

predicate map_count (m: map int int) (a: array int) (lo hi: int) =
  0 <= lo /\ hi <= length a /\
  (forall v: int. Map.get m v = count_occ a lo hi v)
```

This enables the canonical sorting-is-a-permutation proof:

```python
#@ ghost freq_before : dict = \empty_map
#@ ghost freq_after : dict = \empty_map
# ... populate freq_before from arr before sorting ...
# ... sort arr ...
# ... populate freq_after from arr after sorting ...
#@ ensures \map_eq(freq_before, freq_after)
```

#### 6b. `\map_sum(m, lo, hi)` — sum of map values

```python
#@ ensures \map_sum(counts, 0, 256) == n
```

**Why3 logic function:**

```why3
let rec ghost function map_sum (m: map int int) (lo hi: int) : int
  variant { hi - lo }
= if lo >= hi then 0
  else Map.get m lo + map_sum m (lo + 1) hi
```

These are optional — can be deferred to a follow-up.

### Phase 7 — Tests

1. **Parser test**: verify `\empty_map`, `\const_map(0)`,
   `\map_get(m, k)`, `\map_set(m, k, v)`, `\map_eq(m1, m2)`,
   `\map_dom(m, k)`.

2. **End-to-end reference test — frequency counting:**

```python
#@ requires n >= 0
#@ requires \length(arr) >= n
#@ ensures \map_get(freq, 0) >= 0
#@ assigns \nothing
def count_zeros(arr: list, n: int) -> int:
    #@ ghost freq : dict = \empty_map
    count: int = 0
    i: int = 0
    while i < n:
        #@ loop invariant 0 <= i and i <= n
        #@ loop invariant count >= 0
        #@ loop invariant count == \map_get(freq, 0)
        #@ loop variant n - i
        if arr[i] == 0:
            count = count + 1
            #@ ghost freq = \map_set(freq, 0, \map_get(freq, 0) + 1)
        i = i + 1
    return count
```

3. **End-to-end reference test — map as visited set:**

```python
#@ requires n >= 0
#@ requires \length(arr) >= n
#@ ensures \result >= 0
#@ assigns \nothing
def count_unique(arr: list, n: int) -> int:
    #@ ghost visited : dict = \empty_map
    count: int = 0
    i: int = 0
    while i < n:
        #@ loop invariant 0 <= i and i <= n
        #@ loop invariant count >= 0
        #@ loop variant n - i
        if arr[i] >= 0:
            #@ ghost visited = \map_set(visited, arr[i], 1)
            count = count + 1
        i = i + 1
    return count
```

4. **End-to-end reference test — const_map:**

```python
#@ requires 1 == 1
#@ ensures \result == 42
#@ assigns \nothing
def const_map_test(k: int) -> int:
    #@ ghost m : dict = \const_map(42)
    #@ assert \map_get(m, k) == 42
    #@ assert \map_get(m, 0) == 42
    #@ assert \map_get(m, 999) == 42
    return 42
```

### Phase 8 — Documentation

1. Update `config/skills/pycsl-annotate/SKILL.md`:
   - Add ghost dict syntax
   - Add `\empty_map`, `\const_map`, `\map_get`, `\map_set`,
     `\map_eq`, `\map_dom`
   - Add frequency counting pattern as worked example

2. Update `config/skills/contract-writer/SKILL.md`:
   - Add `dict` to allowed ghost types
   - Document map operations

3. Update `config/skills/invariant-writer/SKILL.md`:
   - Ghost dicts in loop invariants
   - Counting invariant pattern:
     `\map_get(freq, v) == count_occ(arr, 0, i, v)`

---

## Dependency Graph

```
Phase 1 (Grammar & AST) ← shared GHOST_TYPE rule
    ↓
Phase 2 (Weaver) ← no change
    ↓
Phase 3 (Semantic analysis)
    ↓
Phase 4 (IR emission)
    ↓
Phase 5 (Transpiler) ← medium change
    ↓
Phase 6 (Higher-level predicates) ← optional
    ↓
Phase 7 (Tests)
    ↓
Phase 8 (Documentation)
```

### Shared infrastructure with other ghost-type plans

| Component | Shared? |
|-----------|:-------:|
| `declared_type` field on `GhostAssignDecl` | ✓ |
| `GHOST_TYPE` terminal | ✓ (add `"dict"`) |
| Module4 type dispatch | ✓ (add `"dict"` branch) |
| Module5 `ghost_type` IR field | ✓ |
| Module6 ghost emit dispatcher | ✓ (add `"dict"` branch) |

---

## Why3 `map.Map` Reference

| Function | Signature | Description |
|----------|-----------|-------------|
| `Map.get` | `map 'a 'b → 'a → 'b` | Read key |
| `Map.set` | `map 'a 'b → 'a → 'b → map 'a 'b` | Functional update |
| `Const.const` | `'b → map 'a 'b` | Constant map (all keys → v) |

**Axioms** (built-in to Why3):
```why3
axiom Select_eq : forall m k v. Map.get (Map.set m k v) k = v
axiom Select_neq : forall m k1 k2 v. k1 <> k2 ->
                    Map.get (Map.set m k1 v) k2 = Map.get m k2
```

These two axioms are sufficient for SMT solvers to reason about
map reads and writes efficiently. They are part of the SMT-LIB
`ArraysEx` theory, natively supported by Z3 and Alt-Ergo.

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| SMT timeout on quantified map properties | Medium | `Map.get`/`Map.set` is the best-supported SMT theory (arrays); unlikely to timeout |
| Confusion with Python `dict` (partial, KeyError) | Medium | Document: ghost dicts are total (default 0), not partial |
| `map.Map` import conflict in typed/store model | Low | Typed/store already imports `map.Map` — ghost dict uses same module, no conflict |
| Extensional equality explosion | Low | `Map.get (Map.set ...)` chains are bounded; SMT handles well |
| Backward compatibility | None | No existing code uses ghost dicts |

---

## Impact on Verification Capabilities

### Before (current)

- Python `dict` → abstract `val dict_new () : int` — no reasoning
  about contents possible in hoare model.
- Counting, frequency tables, visited sets cannot be expressed in
  contracts.
- Permutation proof requires ghost arrays (`ghost-array.md`) but
  cannot use multiset/frequency-table approach.

### After (with ghost dicts)

```python
# Frequency table — prove sorting preserves multiset
#@ ghost freq : dict = \empty_map
#@ loop invariant \map_get(freq, arr[j]) == count_of(arr, 0, i, arr[j])

# Visited set — prove all elements processed
#@ ghost seen : dict = \empty_map
#@ ensures \map_dom(seen, target)

# Inverse mapping — prove bijection
#@ ghost inverse : dict = \empty_map
#@ ensures \map_get(inverse, arr[i]) == i
```

### Comparison with other tools

| Tool | Ghost maps | Operations | Totality |
|------|:---------:|:----------:|:--------:|
| Frama-C/ACSL | ✗ (use `\lambda` logic) | N/A | N/A |
| Dafny | ✓ (`ghost var m: map<int,int>`) | `m[k]`, `m[k := v]`, `k in m` | Partial (`k in m` required) |
| Why3 | ✓ (`map int int`) | `Map.get`, `Map.set`, `Const.const` | Total (default-valued) |
| Viper | ✓ (`Map[Int, Int]`) | `m[k]`, `m[k := v]` | Partial |
| **PyCSL (current)** | **✗** | **✗** | N/A |
| **PyCSL (after)** | **✓** | `\map_get`, `\map_set`, `\const_map`, `\map_eq`, `\map_dom` | Total (default 0) |

---

## Estimated Scope

| Phase | Files changed | Complexity |
|-------|:---:|---|
| 1. Grammar & AST | 1 | Small — 6 expression nodes + grammar rules |
| 2. Weaver | 0 | None |
| 3. Semantic analysis | 1 | Small — type dispatch |
| 4. IR emission | 1 | Small — 6 IR handlers |
| 5. Transpiler | 1 | Medium — ghost dict declaration, 6 expression handlers, preamble import |
| 6. Higher-level predicates | 1 | Medium — `\map_count` logic function (optional) |
| 7. Tests | 2–4 | Medium — parser + 3 end-to-end tests |
| 8. Documentation | 2–3 | Small — skill updates |

### SMT solver advantage

Ghost dicts map directly to SMT-LIB's `(Array Int Int)` theory —
the **best-supported theory** across all SMT solvers. Z3 and Alt-Ergo
both handle `select`/`store` (= `Map.get`/`Map.set`) natively with
dedicated decision procedures. Ghost dict VCs will typically be
**faster** to discharge than array or list VCs.
