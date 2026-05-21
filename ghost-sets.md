# Ghost Set Variables — Implementation Plan

## Problem Statement

PyCSL ghost variables are currently **integer-only**. Ghost sets
would let contracts track membership, coverage, uniqueness, and
partition properties — fundamental building blocks for verifying
search, filtering, graph traversal, and deduplication algorithms.

### Why sets, not ghost dicts?

Ghost dictionaries (`ghost-dictionnaries.md`) model finite maps
`int → int`. Ghost sets model **membership**: "is element x in the
set?" They share the same underlying Why3 theory (`map int bool`)
but provide a **higher-level, set-theoretic API** that is more
natural for specification patterns:

| | Ghost dict | Ghost set |
|---|---|---|
| Why3 model | `map int int` | `map int bool` (characteristic fn) |
| Question answered | "what is the value for key k?" | "is element x in the set?" |
| Typical use | frequency table, inverse map | visited nodes, coverage, uniqueness |
| Operations | `\map_get`, `\map_set` | `\set_mem`, `\set_add`, `\set_union`, `\set_card` |

Ghost sets could be implemented as a thin layer on top of ghost
dicts (with values restricted to 0/1). However, using `map int bool`
with a set-theoretic API produces cleaner specifications and
stronger SMT automation (boolean reasoning vs. integer comparison).

### Motivating examples

**1. Track visited elements (graph traversal):**

```python
#@ ghost visited : set = \set_empty
while queue_size > 0:
    #@ loop invariant \set_card(visited) <= i
    node: int = queue[front]
    #@ ghost visited = \set_add(visited, node)
    ...
```

**2. Prove all elements processed:**

```python
#@ ghost processed : set = \set_empty
i: int = 0
while i < n:
    #@ loop invariant \forall j; 0 <= j and j < i ==> \set_mem(arr[j], processed)
    #@ ghost processed = \set_add(processed, arr[i])
    ...
```

**3. Prove uniqueness (no duplicates):**

```python
#@ ghost seen : set = \set_empty
i: int = 0
while i < n:
    #@ loop invariant \set_card(seen) == i   # each element was new
    if not \set_mem(arr[i], seen):
        #@ ghost seen = \set_add(seen, arr[i])
        count = count + 1
    ...
```

**4. Partition property:**

```python
#@ ghost evens : set = \set_empty
#@ ghost odds : set = \set_empty
#@ ensures \set_inter(evens, odds) == \set_empty
#@ ensures \set_card(evens) + \set_card(odds) == n
```

### Target syntax

```python
#@ ghost s : set = \set_empty                     # empty set
#@ ghost s = \set_add(s, x)                      # add element
#@ ghost s = \set_remove(s, x)                   # remove element
#@ ghost s = \set_union(s1, s2)                  # union
#@ ghost s = \set_inter(s1, s2)                  # intersection
#@ ghost s = \set_diff(s1, s2)                   # difference
#@ ensures \set_mem(x, s)                        # membership test
#@ ensures \set_card(s) == n                     # cardinality
#@ ensures \set_subset(s1, s2)                   # subset test
#@ ensures \set_eq(s1, s2)                       # equality
#@ ensures s == \set_empty                       # emptiness test
```

### Why3 target — characteristic function model

```why3
use map.Map
use map.Const

(* Ghost set = map int bool, where true = member *)
let ghost s = ref (Const.const false : map int bool) in

(* add *)
ghost s := Map.set !s x true;

(* remove *)
ghost s := Map.set !s x false;

(* membership *)
assert { Map.get !s x = true };

(* cardinality, union, inter — via preamble logic functions *)
```

**Why `map int bool` instead of Why3's `set.Fset`?**

Why3's `set.Fset` uses an abstract type with axiomatized operations.
While elegant, it requires cloning and instantiation for concrete
element types. The `map int bool` approach:
- Uses the same `map.Map` module as ghost dicts (no new imports)
- Maps directly to SMT-LIB's `(Array Int Bool)` theory
- Allows element-level reasoning via `Map.get`/`Map.set` axioms
- Cardinality requires a custom logic function (see Phase 6)

---

## Current State (per module)

| Module | Set support today | Ghost support today |
|--------|------------------|-------------------|
| **Module2** (Parser) | No set-specific contract syntax | Untyped, int only |
| **Module4** (Semantic) | Knows `set`/`frozenset` from type annotations | Ghost: hard-coded `int` |
| **Module5** (IR Emitter) | `{"type":"SetLit", "elts":[...]}` | Ghost IR: no type field |
| **Module6** (Transpiler) | `SetLit` → `val set_new (x: int) : int` (abstract); `set()` → `val set_empty () : int` (abstract) | Ghost: `ref int` only; **set values → `0`** in assign |

Like dicts, sets are currently **opaque** in hoare model — no
reasoning about membership or cardinality is possible.

---

## Design Decisions

### D1. `map int bool` — characteristic function model

A ghost set S is represented as `map int bool`:
- `Map.get S x = true` means x ∈ S
- `Map.get S x = false` means x ∉ S
- `Const.const false` is the empty set

This is the standard representation in automated verification
(Boogie, Viper, Why3). SMT solvers handle `(Array Int Bool)`
natively.

### D2. Storage model: ref-wrapped

Like ghost dicts, ghost sets are ref-wrapped:

```why3
let ghost s = ref (Const.const false : map int bool) in
ghost s := Map.set !s x true;
```

### D3. Set operations as logic functions

Union, intersection, difference, cardinality, and subset are
emitted as **logic functions** in the WhyML preamble (not as
Why3 stdlib imports). This avoids dependency on `set.Fset` and
keeps the model self-contained:

```why3
predicate set_mem (s: map int bool) (x: int) = Map.get s x = true

function set_add (s: map int bool) (x: int) : map int bool =
  Map.set s x true

function set_remove (s: map int bool) (x: int) : map int bool =
  Map.set s x false

predicate set_subset (s1 s2: map int bool) =
  forall x: int. Map.get s1 x = true -> Map.get s2 x = true

predicate set_eq (s1 s2: map int bool) =
  forall x: int. Map.get s1 x = Map.get s2 x
```

Union, intersection, and difference require quantifier-based
definitions:

```why3
(* Cannot be expressed as Map operations directly — use predicates *)
predicate set_union_is (u s1 s2: map int bool) =
  forall x: int. Map.get u x = true <-> (Map.get s1 x = true \/ Map.get s2 x = true)

predicate set_inter_is (i s1 s2: map int bool) =
  forall x: int. Map.get i x = true <-> (Map.get s1 x = true /\ Map.get s2 x = true)
```

For **constructive** union/inter/diff (returning a new set), we use
`val` declarations with postconditions:

```why3
val set_union (s1 s2: map int bool) : map int bool
  ensures { forall x: int. Map.get result x = true <->
            (Map.get s1 x = true \/ Map.get s2 x = true) }

val set_inter (s1 s2: map int bool) : map int bool
  ensures { forall x: int. Map.get result x = true <->
            (Map.get s1 x = true /\ Map.get s2 x = true) }

val set_diff (s1 s2: map int bool) : map int bool
  ensures { forall x: int. Map.get result x = true <->
            (Map.get s1 x = true /\ Map.get s2 x = false) }
```

### D4. Cardinality

Cardinality (`\set_card`) is the most challenging operation. Over
`map int bool` (infinite domain), cardinality is only well-defined
for **finitely-supported** maps (finitely many keys set to `true`).

Approach: bounded cardinality via a recursive counting function
over a known range:

```why3
let rec ghost function set_card_range (s: map int bool) (lo hi: int) : int
  variant { hi - lo }
= if lo >= hi then 0
  else (if Map.get s lo = true then 1 else 0) + set_card_range s (lo + 1) hi
```

Usage: `\set_card(s, lo, hi)` counts elements in [lo, hi). This
is explicit about the counting range and avoids the infinite-domain
problem.

For common patterns (e.g., elements come from `arr[0..n)`), the
user writes:

```python
#@ ensures \set_card(seen, 0, n) == n      # all elements in [0, n) are in the set
```

### D5. Augmented assignment

`+=` on a set ghost means "add element" (shorthand for `\set_add`):

```python
#@ ghost s += x        # equivalent to: ghost s = \set_add(s, x)
```

`-=` on a set ghost means "remove element":

```python
#@ ghost s -= x        # equivalent to: ghost s = \set_remove(s, x)
```

`*=` is rejected.

---

## Implementation Plan

### Phase 1 — Grammar & AST (Module2)

**File: `src/pycsl/Module2_Parser.py`**

1. Extend `GhostAssignDecl` (shared):

```python
declared_type: str  # "int", "string", "array", "list",
                    # "tuple2"..."tuple4", "dict", "set"
```

2. Add built-in expression nodes for set operations:

```lark
| "\\set_empty" -> set_empty_expr
| "\\set_add" "(" expr "," expr ")" -> set_add_expr
| "\\set_remove" "(" expr "," expr ")" -> set_remove_expr
| "\\set_union" "(" expr "," expr ")" -> set_union_expr
| "\\set_inter" "(" expr "," expr ")" -> set_inter_expr
| "\\set_diff" "(" expr "," expr ")" -> set_diff_expr
| "\\set_mem" "(" expr "," expr ")" -> set_mem_expr
| "\\set_card" "(" expr "," expr "," expr ")" -> set_card_expr
| "\\set_subset" "(" expr "," expr ")" -> set_subset_expr
| "\\set_eq" "(" expr "," expr ")" -> set_eq_expr
```

3. AST nodes:

```python
@dataclass
class SetEmptyExpr(CSLNode):
    pass

@dataclass
class SetAddExpr(CSLNode):
    set_expr: CSLNode
    elem: CSLNode

@dataclass
class SetRemoveExpr(CSLNode):
    set_expr: CSLNode
    elem: CSLNode

@dataclass
class SetUnionExpr(CSLNode):
    left: CSLNode
    right: CSLNode

@dataclass
class SetInterExpr(CSLNode):
    left: CSLNode
    right: CSLNode

@dataclass
class SetDiffExpr(CSLNode):
    left: CSLNode
    right: CSLNode

@dataclass
class SetMemExpr(CSLNode):
    elem: CSLNode
    set_expr: CSLNode

@dataclass
class SetCardExpr(CSLNode):
    set_expr: CSLNode
    lo: CSLNode
    hi: CSLNode

@dataclass
class SetSubsetExpr(CSLNode):
    left: CSLNode
    right: CSLNode

@dataclass
class SetEqExpr(CSLNode):
    left: CSLNode
    right: CSLNode
```

### Phase 2 — Weaver (Module3)

No change needed.

### Phase 3 — Semantic analysis (Module4)

**File: `src/pycsl/Module4_SemanticAnalyzer.py`**

1. Register ghost sets in scope:

```python
if ghost_type == "set":
    self.current_scope[ga.target] = "ghost_set"
```

2. Validation:
   - `+=` → allowed (set_add shorthand)
   - `-=` → allowed (set_remove shorthand)
   - `*=` → error
   - Set operations → require set-typed operands

### Phase 4 — IR emission (Module5)

**File: `src/pycsl/Module5_IREmitter.py`**

1. Carry type through IR (shared).

2. Add IR handlers for all set operations:

```python
def _csl_set_empty(self, node) -> Dict[str, Any]:
    return {"type": "SetEmpty"}

def _csl_set_add(self, node) -> Dict[str, Any]:
    return {"type": "SetAdd",
            "set": self._csl_to_ir(node.set_expr),
            "elem": self._csl_to_ir(node.elem)}

def _csl_set_remove(self, node) -> Dict[str, Any]:
    return {"type": "SetRemove",
            "set": self._csl_to_ir(node.set_expr),
            "elem": self._csl_to_ir(node.elem)}

def _csl_set_union(self, node) -> Dict[str, Any]:
    return {"type": "SetUnion",
            "left": self._csl_to_ir(node.left),
            "right": self._csl_to_ir(node.right)}

def _csl_set_inter(self, node) -> Dict[str, Any]:
    return {"type": "SetInter",
            "left": self._csl_to_ir(node.left),
            "right": self._csl_to_ir(node.right)}

def _csl_set_diff(self, node) -> Dict[str, Any]:
    return {"type": "SetDiff",
            "left": self._csl_to_ir(node.left),
            "right": self._csl_to_ir(node.right)}

def _csl_set_mem(self, node) -> Dict[str, Any]:
    return {"type": "SetMem",
            "elem": self._csl_to_ir(node.elem),
            "set": self._csl_to_ir(node.set_expr)}

def _csl_set_card(self, node) -> Dict[str, Any]:
    return {"type": "SetCard",
            "set": self._csl_to_ir(node.set_expr),
            "lo": self._csl_to_ir(node.lo),
            "hi": self._csl_to_ir(node.hi)}

def _csl_set_subset(self, node) -> Dict[str, Any]:
    return {"type": "SetSubset",
            "left": self._csl_to_ir(node.left),
            "right": self._csl_to_ir(node.right)}

def _csl_set_eq(self, node) -> Dict[str, Any]:
    return {"type": "SetEq",
            "left": self._csl_to_ir(node.left),
            "right": self._csl_to_ir(node.right)}
```

### Phase 5 — WhyML transpiler (Module6)

**File: `src/pycsl/Module6_WhyMLTranspiler.py`**

#### 5a. Ghost set declaration

In `_handle_ghost_assign_stmt`:

```python
if ghost_type == "set":
    self._ghost_set_vars.add(target)

    if target not in declared_refs:
        declared_refs.add(target)
        local_refs.add(target)
        rest_code = self._stmts_to_whyml(rest, ...)
        if not rest_code:
            rest_code = f"{indent}()"

        val_ir = stmt.get("value", {})
        if val_ir.get("type") == "SetEmpty":
            set_init = "(Const.const false : map int bool)"
        else:
            set_init = self._expr_to_whyml(stmt["value"], local_refs)

        return (f"{indent}let ghost {safe_target} = "
                f"ref {set_init} in\n{rest_code}")

    # Reassignment
    if op == "+=":
        # Shorthand for set_add
        elem = self._expr_to_whyml(stmt["value"], local_refs)
        code = (f"{indent}ghost {safe_target} := "
                f"Map.set !{safe_target} {elem} true")
    elif op == "-=":
        # Shorthand for set_remove
        elem = self._expr_to_whyml(stmt["value"], local_refs)
        code = (f"{indent}ghost {safe_target} := "
                f"Map.set !{safe_target} {elem} false")
    else:
        val_whyml = self._expr_to_whyml(stmt["value"], local_refs)
        code = f"{indent}ghost {safe_target} := {val_whyml}"
    if rest:
        code += ";\n" + self._stmts_to_whyml(rest, ...)
    return code
```

#### 5b. Set expression handlers

Add to `_expr_to_whyml` dispatch:

```python
if t == "SetEmpty":
    return "(Const.const false : map int bool)"

if t == "SetAdd":
    s = self._expr_to_whyml(ir_expr["set"], local_refs, ...)
    e = self._expr_to_whyml(ir_expr["elem"], local_refs, ...)
    return f"(Map.set {s} {e} true)"

if t == "SetRemove":
    s = self._expr_to_whyml(ir_expr["set"], local_refs, ...)
    e = self._expr_to_whyml(ir_expr["elem"], local_refs, ...)
    return f"(Map.set {s} {e} false)"

if t == "SetMem":
    e = self._expr_to_whyml(ir_expr["elem"], local_refs, ...)
    s = self._expr_to_whyml(ir_expr["set"], local_refs, ...)
    return f"(Map.get {s} {e} = true)"

if t == "SetUnion":
    l = self._expr_to_whyml(ir_expr["left"], local_refs, ...)
    r = self._expr_to_whyml(ir_expr["right"], local_refs, ...)
    return f"(pycsl_set_union {l} {r})"

if t == "SetInter":
    l = self._expr_to_whyml(ir_expr["left"], local_refs, ...)
    r = self._expr_to_whyml(ir_expr["right"], local_refs, ...)
    return f"(pycsl_set_inter {l} {r})"

if t == "SetDiff":
    l = self._expr_to_whyml(ir_expr["left"], local_refs, ...)
    r = self._expr_to_whyml(ir_expr["right"], local_refs, ...)
    return f"(pycsl_set_diff {l} {r})"

if t == "SetCard":
    s = self._expr_to_whyml(ir_expr["set"], local_refs, ...)
    lo = self._expr_to_whyml(ir_expr["lo"], local_refs, ...)
    hi = self._expr_to_whyml(ir_expr["hi"], local_refs, ...)
    return f"(pycsl_set_card {s} {lo} {hi})"

if t == "SetSubset":
    l = self._expr_to_whyml(ir_expr["left"], local_refs, ...)
    r = self._expr_to_whyml(ir_expr["right"], local_refs, ...)
    return f"(pycsl_set_subset {l} {r})"

if t == "SetEq":
    l = self._expr_to_whyml(ir_expr["left"], local_refs, ...)
    r = self._expr_to_whyml(ir_expr["right"], local_refs, ...)
    return f"({l} = {r})"
```

Note: `\set_mem` and `\set_add`/`\set_remove` compile directly to
`Map.get`/`Map.set` (no preamble function needed). Union, inter,
diff, card, and subset require preamble logic functions.

#### 5c. Ghost set variable tracking

1. Add `self._ghost_set_vars: Set[str] = set()` to
   `_reset_function_state`.

2. Ghost set vars use `!` dereference (ref-wrapped).

3. Exclude from parameter lists.

#### 5d. Preamble logic functions

When ghost sets are used, emit the following in the preamble:

```python
# In _emit_preamble:
if needs.get("needs_ghost_set"):
    out.append("  use map.Map")
    out.append("  use map.Const")
    out.append("")

if needs.get("needs_set_union"):
    out.append("  val ghost function pycsl_set_union "
               "(s1 s2: map int bool) : map int bool")
    out.append("    ensures { forall x: int. "
               "Map.get result x = true <-> "
               "(Map.get s1 x = true \\/ Map.get s2 x = true) }")
    out.append("")

if needs.get("needs_set_inter"):
    out.append("  val ghost function pycsl_set_inter "
               "(s1 s2: map int bool) : map int bool")
    out.append("    ensures { forall x: int. "
               "Map.get result x = true <-> "
               "(Map.get s1 x = true /\\ Map.get s2 x = true) }")
    out.append("")

if needs.get("needs_set_diff"):
    out.append("  val ghost function pycsl_set_diff "
               "(s1 s2: map int bool) : map int bool")
    out.append("    ensures { forall x: int. "
               "Map.get result x = true <-> "
               "(Map.get s1 x = true /\\ Map.get s2 x = false) }")
    out.append("")

if needs.get("needs_set_subset"):
    out.append("  predicate pycsl_set_subset "
               "(s1 s2: map int bool) =")
    out.append("    forall x: int. "
               "Map.get s1 x = true -> Map.get s2 x = true")
    out.append("")

if needs.get("needs_set_card"):
    out.append("  let rec ghost function pycsl_set_card "
               "(s: map int bool) (lo hi: int) : int")
    out.append("    variant { hi - lo }")
    out.append("  = if lo >= hi then 0")
    out.append("    else (if Map.get s lo = true then 1 else 0) "
               "+ pycsl_set_card s (lo + 1) hi")
    out.append("")
    # Useful lemma: adding a fresh element increments cardinality
    out.append("  let rec lemma pycsl_set_card_add "
               "(s: map int bool) (lo hi x: int) : unit")
    out.append("    requires { lo <= x < hi }")
    out.append("    requires { Map.get s x = false }")
    out.append("    variant { hi - lo }")
    out.append("    ensures { pycsl_set_card (Map.set s x true) lo hi "
               "= pycsl_set_card s lo hi + 1 }")
    out.append("  = if lo < hi - 1 then begin")
    out.append("      if lo = x then ()")
    out.append("      else pycsl_set_card_add s (lo + 1) hi x")
    out.append("    end")
    out.append("")
```

#### 5e. Coexistence with ghost dicts

Ghost sets use `map int bool` while ghost dicts use `map int int`.
Both import `map.Map` and `map.Const`. Why3 handles polymorphic
maps natively — `map int bool` and `map int int` are distinct types,
no conflict.

The preamble scanner must track both:
```python
needs_map_ghost = needs.get("needs_ghost_set") or needs.get("needs_ghost_dict")
if needs_map_ghost:
    out.append("  use map.Map")
    out.append("  use map.Const")
```

---

### Phase 6 — Array-to-set conversion

#### 6a. `\to_set(arr, lo, hi)` — array slice → set

Build a ghost set containing all elements of `arr[lo..hi)`:

```python
#@ ghost elements : set = \to_set(arr, 0, n)
#@ ensures \set_mem(target, elements)   # target is in the array
```

**Why3 logic function:**

```why3
let rec ghost function pycsl_to_set (a: array int) (lo hi: int) : map int bool
  requires { 0 <= lo }
  requires { hi <= length a }
  variant { hi - lo }
= if lo >= hi then (Const.const false : map int bool)
  else Map.set (pycsl_to_set a (lo + 1) hi) a[lo] true
```

This is optional but covers a very common pattern.

### Phase 7 — Tests

1. **Parser test**: verify all 10 expression forms parse.

2. **End-to-end reference test — membership tracking:**

```python
#@ requires n >= 0
#@ requires \length(arr) >= n
#@ requires n > 0
#@ ensures \set_mem(arr[0], seen)
#@ assigns \nothing
def track_first(arr: list, n: int) -> int:
    #@ ghost seen : set = \set_empty
    i: int = 0
    while i < n:
        #@ loop invariant 0 <= i and i <= n
        #@ loop invariant i > 0 ==> \set_mem(arr[0], seen)
        #@ loop variant n - i
        #@ ghost seen = \set_add(seen, arr[i])
        i = i + 1
    return 0
```

3. **End-to-end reference test — += shorthand:**

```python
#@ requires \length(arr) >= 2
#@ ensures \set_mem(arr[0], s)
#@ ensures \set_mem(arr[1], s)
#@ assigns \nothing
def add_two(arr: list) -> int:
    #@ ghost s : set = \set_empty
    #@ ghost s += arr[0]
    #@ ghost s += arr[1]
    return 0
```

4. **End-to-end reference test — cardinality:**

```python
#@ requires 1 == 1
#@ ensures \result == 0
#@ assigns \nothing
def card_test() -> int:
    #@ ghost s : set = \set_empty
    #@ ghost s = \set_add(s, 3)
    #@ ghost s = \set_add(s, 5)
    #@ assert \set_card(s, 0, 10) == 2
    return 0
```

### Phase 8 — Documentation

1. Update `config/skills/pycsl-annotate/SKILL.md`:
   - Add ghost set syntax + all 10 operations
   - Add membership-tracking pattern as worked example
   - Document `\set_card` range requirement

2. Update `config/skills/contract-writer/SKILL.md`:
   - Add `set` to allowed ghost types
   - Document set operations and `+=`/`-=` shorthands

3. Update `config/skills/invariant-writer/SKILL.md`:
   - Ghost sets in loop invariants
   - Coverage invariant pattern:
     `\forall j; 0 <= j and j < i ==> \set_mem(arr[j], processed)`

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
Phase 5 (Transpiler) ← medium-large change (preamble logic fns)
    ↓
Phase 6 (\to_set conversion) ← optional
    ↓
Phase 7 (Tests)
    ↓
Phase 8 (Documentation)
```

### Shared infrastructure

All 6 ghost type plans (string, array, list, tuple, dict, set)
share:
- `declared_type` field on `GhostAssignDecl`
- `GHOST_TYPE` terminal in grammar
- Module4 type dispatch
- Module5 `ghost_type` IR field
- Module6 ghost emit dispatcher

Ghost sets and ghost dicts additionally share the `map.Map` +
`map.Const` imports — the preamble scanner should track a single
`needs_map` flag that covers both.

---

## Why3 Semantics Reference

| Operation | PyCSL syntax | Why3 output |
|-----------|-------------|-------------|
| Empty set | `\set_empty` | `(Const.const false : map int bool)` |
| Add | `\set_add(s, x)` | `(Map.set s x true)` |
| Remove | `\set_remove(s, x)` | `(Map.set s x false)` |
| Membership | `\set_mem(x, s)` | `(Map.get s x = true)` |
| Union | `\set_union(s1, s2)` | `(pycsl_set_union s1 s2)` — val with postcondition |
| Intersection | `\set_inter(s1, s2)` | `(pycsl_set_inter s1 s2)` — val with postcondition |
| Difference | `\set_diff(s1, s2)` | `(pycsl_set_diff s1 s2)` — val with postcondition |
| Cardinality | `\set_card(s, lo, hi)` | `(pycsl_set_card s lo hi)` — recursive ghost function |
| Subset | `\set_subset(s1, s2)` | `(pycsl_set_subset s1 s2)` — predicate |
| Equality | `\set_eq(s1, s2)` | `(s1 = s2)` — extensional equality |

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Quantified union/inter may timeout | Medium | `val ghost function` with postcondition lets SMT reason without unfolding; test with small sets first |
| `\set_card` recursive function may timeout on large ranges | Medium | Provide `pycsl_set_card_add` lemma; limit ranges in tests |
| `map int bool` vs `map int int` type confusion | Low | Different types in Why3 — compiler catches misuse |
| `\set_card` range semantics unfamiliar to users | Low | Document clearly; provide `\to_set` for common patterns |
| Backward compatibility | None | No existing code uses ghost sets |

---

## Comparison with Other Tools

| Tool | Ghost sets | Membership | Cardinality | Set algebra |
|------|:---------:|:----------:|:-----------:|:-----------:|
| Frama-C/ACSL | ✗ (use `\numof`) | N/A | Via `\numof` | N/A |
| Dafny | ✓ (`ghost var s: set<int>`) | `x in s` | `|s|` | `+`, `*`, `-` |
| Why3 | ✓ (`set.Fset`) | `Fset.mem` | `Fset.cardinal` | `Fset.union`, etc. |
| Viper | ✓ (`Set[Int]`) | `x in s` | `|s|` | `union`, `intersection` |
| **PyCSL (current)** | **✗** | **✗** | **✗** | **✗** |
| **PyCSL (after)** | **✓** | `\set_mem` | `\set_card` | `\set_union`, `\set_inter`, `\set_diff` |

---

## Estimated Scope

| Phase | Files changed | Complexity |
|-------|:---:|---|
| 1. Grammar & AST | 1 | Medium — 10 expression nodes + grammar rules |
| 2. Weaver | 0 | None |
| 3. Semantic analysis | 1 | Small — type dispatch + validation |
| 4. IR emission | 1 | Medium — 10 IR handlers |
| 5. Transpiler | 1 | Medium-large — ghost set emit, 10 expr handlers, 5+ preamble logic functions with lemmas |
| 6. `\to_set` conversion | 1 | Small — 1 recursive ghost function |
| 7. Tests | 3–4 | Medium — parser + 3 end-to-end tests |
| 8. Documentation | 2–3 | Small — skill updates |
