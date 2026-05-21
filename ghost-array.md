# Ghost Array Variables — Implementation Plan

## Problem Statement

PyCSL ghost variables are currently **integer-only**. Ghost arrays
would let contracts track permutation witnesses, snapshot element
histories, and count distributions — properties that are essential
for verifying sorting algorithms, partitioning, and data structure
operations at the specification level.

### Motivating examples

**1. Permutation tracking for Quicksort:**

```python
#@ ghost perm : array = \old(arr)
#@ ensures \is_permutation(arr, perm, 0, \length(arr))
#@ assigns arr[lo..hi]
def quicksort(arr: list, lo: int, hi: int) -> None:
    ...
```

**2. Element snapshot for in-place reversal:**

```python
#@ ghost snap : array = \copy(arr)
#@ ensures \forall i; 0 <= i and i < n ==> arr[i] == snap[n - 1 - i]
#@ assigns arr[0..n]
def reverse(arr: list, n: int) -> None:
    ...
```

**3. Ghost counters array (bucket counting):**

```python
#@ ghost counts : array = \make(256, 0)
#@ ghost counts[arr[i]] = counts[arr[i]] + 1
```

### Target syntax

```python
#@ ghost snap : array = \copy(arr)       # snapshot an existing array
#@ ghost fresh : array = \make(n, 0)     # fresh array of size n, filled with 0
#@ ghost snap[i] = expr                  # element-wise ghost update
```

### Why3 target

```why3
let ghost snap = Array.copy arr in          (* snapshot *)
let ghost fresh = Array.make n 0 in         (* fresh *)
ghost snap.(i) <- expr;                     (* element update *)
```

---

## Current State (per module)

| Module | Ghost handling | Array handling |
|--------|--------------|----------------|
| **Module2** (Parser) | `ghost CNAME "=" expr` — untyped, no subscript target | `\length(arr)`, `arr[i]`, `\is_sorted(arr, lo, hi)` all parse |
| **Module3** (Weaver) | Passes `GhostAssignDecl` through | Arrays detected at function signature level |
| **Module4** (Semantic) | `scope[ga.target] = "int"` hard-coded | Knows `list`/`dict` types from annotations |
| **Module5** (IR Emitter) | `{"stmt":"GhostAssign", ...}` — no type field | `ArraySet` is a separate IR node for body `arr[i] = v` |
| **Module6** (Transpiler) | `let ghost x = ref val in` — always `ref int` | Full array support: `Array.make`, `arr[i] <- v`, `Array.copy`, `Array.length` |

Key insight: **Why3 already supports ghost arrays** (`let ghost a = Array.make n 0 in`; `ghost a.(i) <- v`). The pipeline just needs to propagate type info and emit the right WhyML.

---

## Design Decisions

### Ghost array storage model

In Why3, ghost arrays are **not ref-wrapped** — they are mutable
array values (like regular arrays). This differs from ghost scalars
(`ref int`) which are ref-wrapped because WhyML requires `!x` for
reading and `x := v` for writing scalar refs.

```why3
(* Ghost scalar — ref-wrapped *)
let ghost counter = ref 0 in
ghost counter := !counter + 1;
assert { !counter = 1 }

(* Ghost array — NOT ref-wrapped, directly mutable *)
let ghost snap = Array.make 10 0 in
ghost snap.(0) <- 42;
assert { snap.(0) = 42 }
```

This means ghost arrays follow the same emit pattern as regular
array parameters (`arr[i] <- v`), not the ghost scalar pattern
(`x := v`).

### Three initialization forms

| Syntax | WhyML output | Use case |
|--------|-------------|----------|
| `#@ ghost a : array = \copy(arr)` | `let ghost a = Array.copy arr in` | Snapshot an existing array |
| `#@ ghost a : array = \make(n, v)` | `let ghost a = Array.make n v in` | Fresh array of given size |
| `#@ ghost a : array = arr`        | `let ghost a = Array.copy arr in` | Shorthand for copy |

### Ghost array update syntax

```python
#@ ghost a[i] = expr       # element-wise update
```

This is parsed as a `GhostArraySet` (distinct from `GhostAssign`)
and emitted as `ghost a.(i) <- expr`.

---

## Implementation Plan

### Phase 1 — Grammar & AST (Module2)

**File: `src/pycsl/Module2_Parser.py`**

1. Extend `GhostAssignDecl` to carry an optional type:

```python
@dataclass
class GhostAssignDecl(CSLNode):
    target: str
    value: CSLNode
    op: str            # "=" or "+=" or "-=" or "*="
    declared_type: str  # "int" (default), "string", or "array"
```

2. Add a new AST node for ghost array element updates:

```python
@dataclass
class GhostArraySetDecl(CSLNode):
    """Represents `ghost arr[idx] = expr` in contracts."""
    target: str        # array name
    index: CSLNode     # index expression
    value: CSLNode     # value expression
```

3. Extend the grammar:

```lark
ghost_assign: "ghost" CNAME "=" expr
            | "ghost" CNAME ":" CNAME "=" expr

ghost_array_set: "ghost" CNAME "[" expr "]" "=" expr
```

Add `ghost_array_set` to the `annotation` alternatives.

4. Add built-in expression nodes for array constructors:

```lark
| "\\copy" "(" CNAME ")" -> copy_expr
| "\\make" "(" expr "," expr ")" -> make_expr
```

AST nodes:

```python
@dataclass
class CopyExpr(CSLNode):
    source: str

@dataclass
class MakeExpr(CSLNode):
    size: CSLNode
    default: CSLNode
```

5. Lark transformer updates:

```python
def ghost_assign(self, items):
    if len(items) == 3:  # typed: ghost name : type = expr
        return GhostAssignDecl(target=str(items[0]),
                               value=items[2], op="=",
                               declared_type=str(items[1]))
    return GhostAssignDecl(target=str(items[0]),
                           value=items[1], op="=",
                           declared_type="int")

def ghost_array_set(self, items):
    return GhostArraySetDecl(target=str(items[0]),
                             index=items[1],
                             value=items[2])

def copy_expr(self, items):
    return CopyExpr(source=str(items[0]))

def make_expr(self, items):
    return MakeExpr(size=items[0], default=items[1])
```

### Phase 2 — Weaver (Module3)

**File: `src/pycsl/Module3_Weaver.py`**

1. Attach `GhostArraySetDecl` alongside `GhostAssignDecl`:

```python
elif isinstance(c, (GhostAssignDecl, GhostArraySetDecl)):
    node.csl_ghost_assigns.append(c)
```

This is a minimal change — both types get attached to the
corresponding statement node the same way.

### Phase 3 — Semantic analysis (Module4)

**File: `src/pycsl/Module4_SemanticAnalyzer.py`**

1. Type-aware ghost scope registration:

```python
for ga in getattr(child, 'csl_ghost_assigns', []):
    if isinstance(ga, GhostArraySetDecl):
        # Array element update — target must already be in scope
        if ga.target not in self.current_scope:
            self._error(f"Ghost array '{ga.target}' used before declaration")
    else:
        ghost_type = getattr(ga, 'declared_type', 'int')
        if ghost_type == "array":
            self.current_scope[ga.target] = "list"
        elif ghost_type == "string":
            self.current_scope[ga.target] = "str"
        else:
            self.current_scope[ga.target] = "int"
```

2. Validate ghost array operations:
   - `+=`, `-=`, `*=` are **rejected** for array-typed ghosts
   - Only `=` (whole-array reassignment) and `[i] =` (element set)
     are allowed

### Phase 4 — IR emission (Module5)

**File: `src/pycsl/Module5_IREmitter.py`**

1. Carry type through ghost IR:

```python
for ga in getattr(stmt, 'csl_ghost_assigns', []):
    if isinstance(ga, GhostArraySetDecl):
        ir_stmts.append({
            "stmt": "GhostArraySet",
            "target": ga.target,
            "index": self._csl_to_ir(ga.index),
            "value": self._csl_to_ir(ga.value),
        })
    else:
        ir_stmts.append({
            "stmt": "GhostAssign",
            "target": ga.target,
            "value": self._csl_to_ir(ga.value),
            "op": ga.op,
            "ghost_type": getattr(ga, 'declared_type', 'int'),
        })
```

2. Add IR handlers for `CopyExpr` and `MakeExpr`:

```python
def _csl_copy(self, node: CopyExpr) -> Dict[str, Any]:
    return {"type": "ArrayCopy", "source": node.source}

def _csl_make(self, node: MakeExpr) -> Dict[str, Any]:
    return {"type": "ArrayMake",
            "size": self._csl_to_ir(node.size),
            "default": self._csl_to_ir(node.default)}
```

Register in dispatch table.

### Phase 5 — WhyML transpiler (Module6)

**File: `src/pycsl/Module6_WhyMLTranspiler.py`**

This is the most substantial phase. Four sub-tasks:

#### 5a. Ghost array declaration emit

In `_handle_ghost_assign_stmt` (~line 1683), add an array branch:

```python
ghost_type = stmt.get("ghost_type", "int")

if target not in declared_refs:
    declared_refs.add(target)
    local_refs.add(target)
    rest_code = self._stmts_to_whyml(rest, ...)
    if not rest_code:
        rest_code = f"{indent}()"

    if ghost_type == "array":
        self._ghost_array_vars.add(target)
        val_ir = stmt.get("value", {})
        if val_ir.get("type") == "ArrayCopy":
            src = self._whyml_ident(val_ir["source"])
            return (f"{indent}let ghost {safe_target} = "
                    f"Array.copy {src} in\n{rest_code}")
        elif val_ir.get("type") == "ArrayMake":
            size = self._expr_to_whyml(val_ir["size"], local_refs)
            default = self._expr_to_whyml(val_ir["default"], local_refs)
            return (f"{indent}let ghost {safe_target} = "
                    f"Array.make {size} {default} in\n{rest_code}")
        else:
            # Bare variable → implicit copy
            src = self._expr_to_whyml(stmt["value"], local_refs)
            return (f"{indent}let ghost {safe_target} = "
                    f"Array.copy {src} in\n{rest_code}")
    # ... existing int/string paths ...
```

Note: ghost arrays are **NOT ref-wrapped** — they emit
`let ghost x = Array.copy ... in`, not `let ghost x = ref ... in`.

#### 5b. Ghost array element update

Add a new handler `_handle_ghost_array_set_stmt`:

```python
def _handle_ghost_array_set_stmt(self, stmt, rest, local_refs,
                                  declared_refs, indent, in_loop):
    target = self._whyml_ident(stmt["target"])
    index = self._expr_to_whyml(stmt["index"], local_refs)
    value = self._expr_to_whyml(stmt["value"], local_refs)
    code = f"{indent}ghost {target}.({index}) <- {value}"
    if rest:
        code += ";\n" + self._stmts_to_whyml(rest, local_refs,
                                              declared_refs, indent, in_loop)
    return code
```

Register in the statement dispatch (~line 2100):

```python
elif s_type == "GhostArraySet":
    return self._handle_ghost_array_set_stmt(stmt, rest, ...)
```

#### 5c. Ghost array variable tracking

1. Add `self._ghost_array_vars: Set[str] = set()` to per-function state
   reset (`_reset_function_state`, ~line 2653).

2. Update `IRScanner.find_ghost_vars` to also scan `GhostArraySet`
   targets (they reference existing ghost arrays but don't declare
   new ones).

3. When emitting variable references, ghost arrays do **not** use
   `!` dereference (they are direct values, not refs):

```python
# In _expr_to_whyml, Var handler:
if name in self._ghost_array_vars:
    return safe   # direct access, no !
```

4. Array subscript access on ghost arrays uses `arr.(i)` syntax
   (already handled by the existing subscript handler for array
   params — just need to ensure ghost arrays are in the array set):

```python
# In _reset_function_state:
self._array_locals.update(self._ghost_array_vars)
```

#### 5d. Expressions in contracts using ghost arrays

Ghost arrays should be usable in `\is_sorted`, `\length`, subscript
access, and `\forall` quantifiers inside `ensures`/`loop invariant`
clauses. Since ghost arrays are emitted as `array int` values (the
same type as regular array params), existing contract expression
handlers already work — they just need to recognize ghost array
names as arrays.

Ensure `_ghost_array_vars` is consulted wherever
`_current_array1d_params` is checked. The cleanest approach:

```python
# After _reset_function_state:
self._current_array1d_params |= self._ghost_array_vars
```

This makes all existing array contract builtins (`\length`,
`\is_sorted`, subscript) work on ghost arrays automatically.

#### 5e. Auto-import `array.Array`

Ghost arrays always require `use array.Array`. Extend the preamble
scanner to set `needs_array = True` when any function contains ghost
array declarations:

```python
# In _scan_preamble_needs:
for body in all_bodies:
    if self._has_ghost_array(body):
        needs_array = True
```

Where `_has_ghost_array` scans for `GhostAssign` nodes with
`ghost_type == "array"` or `GhostArraySet` nodes.

### Phase 6 — Contract builtins (new predicates)

Add array-specific contract predicates useful with ghost arrays:

#### 6a. `\is_permutation(a, b, lo, hi)`

Asserts that `a[lo..hi)` is a permutation of `b[lo..hi)`.

**Grammar:**
```lark
| "\\is_permutation" "(" CNAME "," CNAME "," expr "," expr ")" -> is_permutation_expr
```

**Why3 logic function** (emitted in preamble when used):
```why3
predicate is_permutation (a b: array int) (lo hi: int) =
  lo <= hi /\ 0 <= lo /\ hi <= Array.length a /\ hi <= Array.length b /\
  (forall v: int.
    count a lo hi v = count b lo hi v)

function count (a: array int) (lo hi v: int) : int =
  if lo >= hi then 0
  else (if a[hi-1] = v then 1 else 0) + count a lo (hi-1) v
```

This is a standard combinatorial property. Z3 can discharge
VCs involving `is_permutation` with appropriate `count` lemmas.

#### 6b. `\copy(arr)` and `\make(n, v)` in contracts

Already added in Phase 1 as expression constructors. In contracts
(spec context), they emit `Array.copy arr` and `Array.make n v`.

#### 6c. `\swap(a, i, j)`

A ghost operation that swaps two elements. Useful as a building
block for sorting proofs:

```python
#@ ghost \swap(arr, i, j)
```

Emits:
```why3
ghost (let tmp = arr.(i) in arr.(i) <- arr.(j); arr.(j) <- tmp)
```

This could be a Phase 2 enhancement (not essential for initial
implementation).

### Phase 7 — Tests

1. **Parser test**: verify parsing of all three initialization forms
   and element update syntax.

2. **End-to-end reference test** (`test-suite/corpus/pycsl-reference/`):

```python
#@ requires \length(arr) >= 2
#@ ensures arr[0] == \old(arr[1])
#@ ensures arr[1] == \old(arr[0])
#@ assigns arr[0..2]
def swap_first_two(arr: list) -> None:
    #@ ghost snap : array = \copy(arr)
    tmp: int = arr[0]
    arr[0] = arr[1]
    arr[1] = tmp
    #@ assert arr[0] == snap[1]
    #@ assert arr[1] == snap[0]
```

3. **Permutation reference test** (if `\is_permutation` is added):

```python
#@ requires \length(arr) >= 2
#@ ensures \is_permutation(arr, snap, 0, 2)
#@ assigns arr[0..2]
def swap_first_two_perm(arr: list) -> None:
    #@ ghost snap : array = \copy(arr)
    tmp: int = arr[0]
    arr[0] = arr[1]
    arr[1] = tmp
```

4. **Ghost array in loop invariant** (sorting):

```python
#@ requires n >= 0
#@ requires \length(arr) >= n
#@ ensures \is_sorted(arr, 0, n)
#@ assigns arr[0..n]
def insertion_sort(arr: list, n: int) -> None:
    #@ ghost original : array = \copy(arr)
    i: int = 1
    while i < n:
        #@ loop invariant 1 <= i and i <= n
        #@ loop invariant \is_sorted(arr, 0, i)
        #@ loop variant n - i
        key: int = arr[i]
        j: int = i - 1
        while j >= 0 and arr[j] > key:
            #@ loop invariant -1 <= j and j < i
            #@ loop invariant \is_sorted(arr, 0, j + 1)
            #@ loop variant j + 1
            arr[j + 1] = arr[j]
            j = j - 1
        arr[j + 1] = key
        i = i + 1
```

### Phase 8 — Documentation

1. Update `config/skills/pycsl-annotate/SKILL.md`:
   - Add ghost array syntax to the annotation reference
   - Add `\copy`, `\make` to the expression list
   - Add `\is_permutation` to the predicate list

2. Update `config/skills/contract-writer/SKILL.md`:
   - Add ghost array types to the allowed types
   - Document `\copy`, `\make`, ghost element update syntax

3. Update `config/skills/invariant-writer/SKILL.md`:
   - Ghost arrays are usable in loop invariants

---

## Dependency Graph

```
Phase 1 (Grammar & AST)
    ↓
Phase 2 (Weaver) ← trivial
    ↓
Phase 3 (Semantic analysis)
    ↓
Phase 4 (IR emission)
    ↓
Phase 5 (Transpiler) ← largest change
    ↓
Phase 6 (Contract builtins) ← \is_permutation is optional
    ↓
Phase 7 (Tests)
    ↓
Phase 8 (Documentation)
```

### Synergy with `ghost-string.md`

Phases 1–4 share the same infrastructure change: adding
`declared_type` to `GhostAssignDecl`. If both ghost strings and
ghost arrays are implemented, they should share:

- The typed ghost grammar rule: `ghost CNAME ":" CNAME "=" expr`
- The `declared_type` field on `GhostAssignDecl`
- The type-dispatch in Module4 and Module6

The two plans diverge at Phase 5 (transpiler emit logic) and
Phase 6 (builtins: `^` / `\str_length` for strings vs.
`\copy` / `\make` / `\is_permutation` for arrays).

---

## Why3 Semantics Reference

| WhyML construct | Meaning |
|----------------|---------|
| `let ghost a = Array.make n v in` | Ghost array, size `n`, all elements `v` |
| `let ghost a = Array.copy b in` | Ghost array, deep copy of `b` |
| `ghost a.(i) <- v` | Ghost element update (no runtime effect) |
| `a.(i)` | Element read (works for ghost and non-ghost) |
| `Array.length a` | Length of array |
| `a == b` | Structural equality (extensional) |

Ghost arrays are erased at extraction — they have no runtime cost.
They exist solely in the verification domain.

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| SMT timeout on `is_permutation` VCs | High | Provide `count` lemmas as Why3 axioms; limit to small arrays in tests |
| Ghost array deref confusion (`!a` vs `a`) | Medium | Ghost arrays are NOT ref-wrapped; careful emit logic + test coverage |
| Interaction with `\old(arr)` | Medium | `\old` already works for array params; ghost arrays initialized at declaration time don't need `\old` |
| `Array.copy` availability | Low | Part of `array.Array` stdlib — always available when `use array.Array` is emitted |
| Backward compatibility | Low | Default `declared_type="int"` preserves all existing tests |

---

## Impact on Verification Capabilities

### Before (current)

Sorting proofs can show `\is_sorted(arr, 0, n)` but **cannot**
express "the output is a permutation of the input" — there is no
way to snapshot the original array.

### After (with ghost arrays)

```python
#@ ghost original : array = \copy(arr)
#@ ensures \is_sorted(arr, 0, n)
#@ ensures \is_permutation(arr, original, 0, n)
```

This is the standard formulation used in Frama-C/ACSL, Dafny,
and Why3 itself for sorting correctness proofs.

### Comparison with other tools

| Tool | Ghost arrays | Permutation predicate |
|------|:-----------:|:---------------------:|
| Frama-C/ACSL | ✓ (`ghost int a[n]`) | ✓ (`\is_permutation`) |
| Dafny | ✓ (`ghost var a := ...`) | ✓ (`multiset(a) == multiset(b)`) |
| Why3 | ✓ (`let ghost a = ...`) | ✓ (user-defined or via `numof`) |
| VeriFast | ✗ (uses separation logic predicates) | ✗ |
| **PyCSL (current)** | **✗** | **✗** |
| **PyCSL (after)** | **✓** | **✓** |

---

## Estimated Scope

| Phase | Files changed | Complexity |
|-------|:---:|---|
| 1. Grammar & AST | 1 | Small — 2 grammar rules, 2 AST nodes, 2 expr nodes |
| 2. Weaver | 1 | Trivial — 1 isinstance check |
| 3. Semantic analysis | 1 | Small — type dispatch + validation |
| 4. IR emission | 1 | Small — 1 new stmt handler + 2 expr handlers |
| 5. Transpiler | 1 | Medium — ghost array declaration, element update, variable tracking |
| 6. Contract builtins | 2 | Medium — `\is_permutation` logic function + `count` axioms |
| 7. Tests | 2–4 | Medium — parser + 2 end-to-end + 1 loop invariant test |
| 8. Documentation | 2–3 | Small — skill updates |
