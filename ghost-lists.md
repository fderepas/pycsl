# Ghost List Variables — Implementation Plan

## Problem Statement

PyCSL ghost variables are currently **integer-only**. Ghost arrays
(see `ghost-array.md`) address mutable, fixed-size snapshots. But
many verification patterns need an **immutable, variable-length
sequence** that grows during execution — a *ghost list*.

Ghost lists are the specification-level counterpart of mathematical
sequences. They enable:

- **Trace/history logging** — append events to a ghost log, prove
  that a protocol was followed in order.
- **Multiset reasoning** — express permutation properties via sorted
  list comparison or bag equivalence.
- **Accumulator specifications** — prove that a loop builds the
  correct sequence element by element.
- **Functional specifications** — state what the output *is* (the
  list of all primes ≤ n) rather than just a property of it.

### Why lists, not just arrays?

| | Ghost array (`ghost-array.md`) | Ghost list (this plan) |
|---|---|---|
| **Why3 type** | `array int` | `list int` |
| **Mutability** | Mutable (in-place `a.(i) <- v`) | Immutable (functional update) |
| **Size** | Fixed at creation | Grows/shrinks via cons/append |
| **Primary use** | Snapshot & compare with original | Build a sequence incrementally |
| **Index access** | O(1) via `a.(i)` | O(n) via `List.nth` |
| **Typical pattern** | `\copy(arr)` before sort | `\cons(x, log)` on each iteration |

### Target syntax

```python
#@ ghost log : list = \nil                    # empty list
#@ ghost log = \cons(x, log)                  # prepend element
#@ ghost log = \append(log, x)               # append element (snoc)
#@ ghost log = \concat(log1, log2)           # concatenate two lists
#@ ensures \list_length(log) == n            # length property
#@ ensures \nth(log, 0) == first_element     # element access
#@ ensures \mem(x, log)                      # membership test
```

### Why3 target

```why3
use list.List
use list.Length
use list.Nth
use list.Mem
use list.Append

let ghost log = ref (Nil : list int) in
ghost log := Cons x !log;                (* prepend *)
ghost log := !log ++ Cons x Nil;         (* append / snoc *)
ghost log := !log ++ !log2;              (* concatenate *)
assert { Length.length !log = n };
assert { nth 0 !log = Some x };
assert { mem x !log };
```

**Critical difference from ghost arrays**: ghost lists are
**ref-wrapped** (`ref (list int)`) because they are immutable values
that get reassigned — unlike arrays which are mutable in place.

---

## Current State (per module)

| Module | Ghost handling | List handling |
|--------|--------------|---------------|
| **Module2** (Parser) | `ghost CNAME "=" expr` — untyped | No `list`-typed contract expressions |
| **Module3** (Weaver) | Pass-through | — |
| **Module4** (Semantic) | `scope[ga.target] = "int"` | `list` type known for `list`-annotated params |
| **Module5** (IR Emitter) | No type field in ghost IR | `ListLit` → `ArrayLit` (erased to array) |
| **Module6** (Transpiler) | `let ghost x = ref val in` — `ref int` only | Python `list` → `array int` (mutable); no `list 'a` type |

Key insight: Why3's `list 'a` is a **completely different type** from
`array 'a`. Python `list` maps to `array int` (mutable, random access).
Ghost lists map to `list int` (immutable, cons-based). These two type
families don't interact in Why3 — conversion requires explicit
`of_list` / `to_list` functions.

---

## Design Decisions

### D1. Storage model: ref-wrapped

Ghost lists are ref-wrapped (`ref (list int)`) because list values are
immutable — to "modify" a list you reassign the ref:

```why3
let ghost log = ref (Nil : list int) in
ghost log := Cons 42 !log;        (* prepend *)
assert { !log = Cons 42 Nil }     (* read via ! *)
```

This matches the ghost scalar pattern (`ref int`), not the ghost array
pattern (direct mutable). Reading uses `!log`, assignment uses
`log := ...`.

### D2. Only int elements

Ghost lists hold `int` elements (`list int`). This matches PyCSL's
uniform `int` type model and avoids polymorphism complications.
Nested lists (`list (list int)`) are out of scope.

### D3. Functional operations only

Ghost lists support only immutable operations:
- `\nil` — empty list
- `\cons(x, xs)` — prepend
- `\append(xs, x)` — append (snoc: `xs ++ Cons x Nil`)
- `\concat(xs, ys)` — concatenation (`xs ++ ys`)
- `\list_length(xs)` — length
- `\nth(xs, i)` — element access (returns int; partial — requires i < length)
- `\mem(x, xs)` — membership test
- `\reverse(xs)` — reverse
- `\hd(xs)` — head element
- `\tl(xs)` — tail (all but first)

No element mutation (`xs[i] = v`) — that's what ghost arrays are for.

### D4. Augmented assignments

Since `\cons` is the most common operation, support the `+=` shorthand:

```python
#@ ghost log += x     # equivalent to: ghost log = \cons(x, log)
```

This is a natural extension: `+=` on a list means "prepend" (the
element `x` is cons'd onto the front). This is analogous to how
`+=` on integers means "add".

Reject `-=` and `*=` on list ghosts.

---

## Implementation Plan

### Phase 1 — Grammar & AST (Module2)

**File: `src/pycsl/Module2_Parser.py`**

1. Extend `GhostAssignDecl` (shared with `ghost-string.md` and
   `ghost-array.md`):

```python
@dataclass
class GhostAssignDecl(CSLNode):
    target: str
    value: CSLNode
    op: str            # "=" or "+="
    declared_type: str  # "int", "string", "array", or "list"
```

2. Add grammar rules for typed ghost declaration (shared):

```lark
ghost_assign: "ghost" CNAME "=" expr
            | "ghost" CNAME ":" CNAME "=" expr
```

3. Add built-in expression nodes for list constructors:

```lark
| "\\nil" -> nil_expr
| "\\cons" "(" expr "," expr ")" -> cons_expr
| "\\append" "(" expr "," expr ")" -> append_expr
| "\\concat" "(" expr "," expr ")" -> concat_expr
| "\\list_length" "(" expr ")" -> list_length_expr
| "\\nth" "(" expr "," expr ")" -> nth_expr
| "\\mem" "(" expr "," expr ")" -> mem_expr
| "\\reverse" "(" expr ")" -> reverse_expr
| "\\hd" "(" expr ")" -> hd_expr
| "\\tl" "(" expr ")" -> tl_expr
```

4. AST nodes:

```python
@dataclass
class NilExpr(CSLNode):
    pass

@dataclass
class ConsExpr(CSLNode):
    head: CSLNode   # element to prepend
    tail: CSLNode   # existing list

@dataclass
class AppendExpr(CSLNode):
    lst: CSLNode    # existing list
    elem: CSLNode   # element to append

@dataclass
class ConcatExpr(CSLNode):
    left: CSLNode
    right: CSLNode

@dataclass
class ListLengthExpr(CSLNode):
    lst: CSLNode

@dataclass
class NthExpr(CSLNode):
    lst: CSLNode
    index: CSLNode

@dataclass
class MemExpr(CSLNode):
    elem: CSLNode
    lst: CSLNode

@dataclass
class ReverseExpr(CSLNode):
    lst: CSLNode

@dataclass
class HdExpr(CSLNode):
    lst: CSLNode

@dataclass
class TlExpr(CSLNode):
    lst: CSLNode
```

### Phase 2 — Weaver (Module3)

No change — `GhostAssignDecl` objects pass through unchanged.

### Phase 3 — Semantic analysis (Module4)

**File: `src/pycsl/Module4_SemanticAnalyzer.py`**

1. Register ghost lists in scope:

```python
ghost_type = getattr(ga, 'declared_type', 'int')
if ghost_type == "list":
    self.current_scope[ga.target] = "ghost_list"
elif ghost_type == "array":
    self.current_scope[ga.target] = "list"   # maps to array int
elif ghost_type == "string":
    self.current_scope[ga.target] = "str"
else:
    self.current_scope[ga.target] = "int"
```

Use `"ghost_list"` to distinguish from `"list"` (which maps to
`array int`). This prevents Module6 from treating ghost lists as
mutable arrays.

2. Type validation:
   - `+=` on list ghost → allowed (cons shorthand)
   - `-=`, `*=` on list ghost → error
   - `\cons`, `\append`, `\concat` → require list operands
   - `\nth`, `\mem`, `\list_length`, etc. → require list operand

### Phase 4 — IR emission (Module5)

**File: `src/pycsl/Module5_IREmitter.py`**

1. Carry `ghost_type` through IR (shared with string/array):

```python
ir_stmts.append({
    "stmt": "GhostAssign",
    "target": ga.target,
    "value": self._csl_to_ir(ga.value),
    "op": ga.op,
    "ghost_type": getattr(ga, 'declared_type', 'int'),
})
```

2. Add IR handlers for each list operation:

```python
def _csl_nil(self, node):
    return {"type": "Nil"}

def _csl_cons(self, node):
    return {"type": "Cons",
            "head": self._csl_to_ir(node.head),
            "tail": self._csl_to_ir(node.tail)}

def _csl_append(self, node):
    return {"type": "ListAppend",
            "list": self._csl_to_ir(node.lst),
            "elem": self._csl_to_ir(node.elem)}

def _csl_concat(self, node):
    return {"type": "ListConcat",
            "left": self._csl_to_ir(node.left),
            "right": self._csl_to_ir(node.right)}

def _csl_list_length(self, node):
    return {"type": "ListLength",
            "list": self._csl_to_ir(node.lst)}

def _csl_nth(self, node):
    return {"type": "ListNth",
            "list": self._csl_to_ir(node.lst),
            "index": self._csl_to_ir(node.index)}

def _csl_mem(self, node):
    return {"type": "ListMem",
            "elem": self._csl_to_ir(node.elem),
            "list": self._csl_to_ir(node.lst)}

def _csl_reverse(self, node):
    return {"type": "ListReverse",
            "list": self._csl_to_ir(node.lst)}

def _csl_hd(self, node):
    return {"type": "ListHd",
            "list": self._csl_to_ir(node.lst)}

def _csl_tl(self, node):
    return {"type": "ListTl",
            "list": self._csl_to_ir(node.lst)}
```

### Phase 5 — WhyML transpiler (Module6)

**File: `src/pycsl/Module6_WhyMLTranspiler.py`**

#### 5a. Ghost list declaration

In `_handle_ghost_assign_stmt` (~line 1683):

```python
if ghost_type == "list":
    self._ghost_list_vars.add(target)
    val_whyml = self._expr_to_whyml_list_ctx(stmt["value"], local_refs)

    if target not in declared_refs:
        declared_refs.add(target)
        local_refs.add(target)
        rest_code = self._stmts_to_whyml(rest, ...)
        if not rest_code:
            rest_code = f"{indent}()"
        return (f"{indent}let ghost {safe_target} = "
                f"ref ({val_whyml} : list int) in\n{rest_code}")

    # Reassignment
    if op == "+=":
        # Shorthand for cons
        elem = self._expr_to_whyml(stmt["value"], local_refs)
        code = f"{indent}ghost {safe_target} := Cons {elem} !{safe_target}"
    else:
        code = f"{indent}ghost {safe_target} := {val_whyml}"
    if rest:
        code += ";\n" + self._stmts_to_whyml(rest, ...)
    return code
```

#### 5b. List expression transpiler

```python
def _expr_to_whyml_list_ctx(self, ir_expr, local_refs):
    """Transpile an expression in list context."""
    if not ir_expr:
        return "Nil"
    t = ir_expr.get("type", "")
    if t == "Nil":
        return "Nil"
    if t == "Cons":
        head = self._expr_to_whyml(ir_expr["head"], local_refs)
        tail = self._expr_to_whyml_list_ctx(ir_expr["tail"], local_refs)
        return f"(Cons {head} {tail})"
    if t == "Var":
        name = ir_expr.get("name", "")
        safe = self._whyml_ident(name)
        if name in self._ghost_list_vars:
            return f"!{safe}"   # deref — lists are ref-wrapped
        return safe
    # Fallback
    return self._expr_to_whyml(ir_expr, local_refs)
```

Add handlers in the main `_expr_to_whyml` dispatch (~line 1290):

```python
if t == "Nil":
    return "Nil"
if t == "Cons":
    head = self._expr_to_whyml(ir_expr["head"], local_refs, ...)
    tail = self._expr_to_whyml(ir_expr["tail"], local_refs, ...)
    return f"(Cons {head} {tail})"
if t == "ListAppend":
    lst = self._expr_to_whyml(ir_expr["list"], local_refs, ...)
    elem = self._expr_to_whyml(ir_expr["elem"], local_refs, ...)
    return f"({lst} ++ Cons {elem} Nil)"
if t == "ListConcat":
    left = self._expr_to_whyml(ir_expr["left"], local_refs, ...)
    right = self._expr_to_whyml(ir_expr["right"], local_refs, ...)
    return f"({left} ++ {right})"
if t == "ListLength":
    lst = self._expr_to_whyml(ir_expr["list"], local_refs, ...)
    return f"(Length.length {lst})"
if t == "ListNth":
    lst = self._expr_to_whyml(ir_expr["list"], local_refs, ...)
    idx = self._expr_to_whyml(ir_expr["index"], local_refs, ...)
    return f"(match Nth.nth {idx} {lst} with None -> 0 | Some v -> v end)"
if t == "ListMem":
    elem = self._expr_to_whyml(ir_expr["elem"], local_refs, ...)
    lst = self._expr_to_whyml(ir_expr["list"], local_refs, ...)
    return f"(Mem.mem {elem} {lst})"
if t == "ListReverse":
    lst = self._expr_to_whyml(ir_expr["list"], local_refs, ...)
    return f"(Reverse.reverse {lst})"
if t == "ListHd":
    lst = self._expr_to_whyml(ir_expr["list"], local_refs, ...)
    return f"(match {lst} with Nil -> 0 | Cons h _ -> h end)"
if t == "ListTl":
    lst = self._expr_to_whyml(ir_expr["list"], local_refs, ...)
    return f"(match {lst} with Nil -> Nil | Cons _ t -> t end)"
```

#### 5c. Ghost list variable tracking

1. Add `self._ghost_list_vars: Set[str] = set()` to
   `_reset_function_state`.

2. Ghost list variables use `!` dereference (they are ref-wrapped,
   like ghost scalars). The existing `_expr_to_whyml` Var handler
   already handles `!` for `local_refs` — ghost list vars must be
   in `local_refs` and in `declared_refs` after declaration.

3. Ghost list variables must NOT appear in the parameter list (same
   exclusion as ghost scalars — already handled by the existing
   `if arg in ghost_vars: continue` check).

#### 5d. Auto-import Why3 list modules

When any function contains ghost list variables, emit the needed
`use` declarations in the preamble:

```python
# In _emit_preamble:
if needs.get("needs_list"):
    out.append("  use list.List")
    out.append("  use list.Length")
    out.append("  use list.Nth")
    out.append("  use list.Mem")
    out.append("  use list.Append")
```

Extend `_scan_preamble_needs` to detect ghost list usage:

```python
needs_list = any(
    self._has_ghost_list(body) for body in all_bodies
) or any(
    self._ir_uses_list_ops(body) for body in all_bodies
)
```

Optionally also add:

```python
if needs.get("needs_list_reverse"):
    out.append("  use list.Reverse")
```

### Phase 6 — Conversion functions (array ↔ list)

For interop between ghost lists and program arrays, provide
conversion builtins:

#### 6a. `\to_list(arr, lo, hi)` — array slice → list

Converts `arr[lo..hi)` to a `list int`.

**Grammar:**
```lark
| "\\to_list" "(" CNAME "," expr "," expr ")" -> to_list_expr
```

**Why3 logic function** (emitted in preamble):
```why3
let rec ghost function array_to_list (a: array int) (lo hi: int) : list int
  requires { 0 <= lo }
  requires { hi <= length a }
  variant { hi - lo }
= if lo >= hi then Nil
  else Cons a[lo] (array_to_list a (lo + 1) hi)
```

Usage:
```python
#@ ghost original : list = \to_list(arr, 0, \length(arr))
# ... sort arr ...
#@ ensures \is_sorted(arr, 0, n)
#@ ensures \list_length(\to_list(arr, 0, n)) == \list_length(original)
```

#### 6b. `\sorted_list(xs)` — check if a list is sorted

**Grammar:**
```lark
| "\\sorted_list" "(" expr ")" -> sorted_list_expr
```

**Why3 predicate:**
```why3
predicate sorted_list (l: list int) =
  match l with
  | Nil -> true
  | Cons _ Nil -> true
  | Cons x (Cons y rest) -> x <= y /\ sorted_list (Cons y rest)
  end
```

#### 6c. `\is_permutation_list(xs, ys)` — permutation via multiset

Uses Why3's `list.Permut` or a custom `count`-based definition:

**Grammar:**
```lark
| "\\is_permutation_list" "(" expr "," expr ")" -> is_permutation_list_expr
```

**Why3 predicate:**
```why3
use list.Permut

(* Or define via counting: *)
predicate is_permutation_list (l1 l2: list int) =
  Length.length l1 = Length.length l2 /\
  (forall x: int. num_occ x l1 = num_occ x l2)
```

### Phase 7 — Worked example: trace verification

A ghost list is ideal for verifying that a state machine follows
a valid protocol:

```python
#@ ghost trace : list = \nil
#@ ensures \list_length(trace) == n
#@ ensures \nth(trace, 0) == 1
#@ assigns \nothing
def process_events(events: list, n: int) -> int:
    result: int = 0
    i: int = 0
    while i < n:
        #@ loop invariant 0 <= i and i <= n
        #@ loop invariant \list_length(trace) == i
        #@ loop variant n - i
        event: int = events[i]
        result = result + event
        #@ ghost trace = \append(trace, event)
        i = i + 1
    return result
```

### Phase 8 — Tests

1. **Parser test**: verify `\nil`, `\cons(x, xs)`, `\append(xs, x)`,
   `\concat(xs, ys)`, `\list_length(xs)`, `\nth(xs, i)`, `\mem(x, xs)`
   all parse correctly.

2. **End-to-end reference test — list construction:**

```python
#@ requires n >= 0
#@ requires \length(arr) >= n
#@ ensures \list_length(trace) == n
#@ assigns \nothing
def sum_with_trace(arr: list, n: int) -> int:
    #@ ghost trace : list = \nil
    result: int = 0
    i: int = 0
    while i < n:
        #@ loop invariant 0 <= i and i <= n
        #@ loop invariant \list_length(trace) == i
        #@ loop variant n - i
        result = result + arr[i]
        #@ ghost trace = \append(trace, arr[i])
        i = i + 1
    return result
```

3. **End-to-end reference test — cons shorthand:**

```python
#@ requires n >= 0
#@ requires \length(arr) >= n
#@ ensures \list_length(stack) == n
#@ assigns \nothing
def build_stack(arr: list, n: int) -> int:
    #@ ghost stack : list = \nil
    i: int = 0
    while i < n:
        #@ loop invariant 0 <= i and i <= n
        #@ loop invariant \list_length(stack) == i
        #@ loop variant n - i
        #@ ghost stack += arr[i]
        i = i + 1
    return 0
```

4. **Membership test:**

```python
#@ requires \length(arr) >= 2
#@ ensures \mem(arr[0], log)
#@ assigns \nothing
def log_two(arr: list) -> int:
    #@ ghost log : list = \nil
    #@ ghost log = \cons(arr[0], log)
    #@ ghost log = \cons(arr[1], log)
    return 0
```

### Phase 9 — Documentation

1. Update `config/skills/pycsl-annotate/SKILL.md`:
   - Add ghost list syntax
   - Add all list builtins (`\nil`, `\cons`, `\append`, etc.)
   - Add `\to_list`, `\sorted_list`, `\is_permutation_list`

2. Update `config/skills/contract-writer/SKILL.md`:
   - Add `list` to allowed ghost types
   - Add list operations to allowed expressions

3. Update `config/skills/invariant-writer/SKILL.md`:
   - Ghost lists in loop invariants
   - `\list_length(trace) == i` as standard counting pattern

---

## Dependency Graph

```
Phase 1 (Grammar & AST) ← shared with ghost-string / ghost-array
    ↓
Phase 2 (Weaver) ← no change
    ↓
Phase 3 (Semantic analysis)
    ↓
Phase 4 (IR emission)
    ↓
Phase 5 (Transpiler) ← largest change
    ↓
Phase 6 (Conversion builtins) ← optional, can defer
    ↓
Phase 7 (Worked example)
    ↓
Phase 8 (Tests)
    ↓
Phase 9 (Documentation)
```

### Shared infrastructure with ghost-string and ghost-array

| Component | Shared? | Detail |
|-----------|:-------:|--------|
| `declared_type` field on `GhostAssignDecl` | ✓ | Same field, new value `"list"` |
| Typed ghost grammar rule | ✓ | `ghost CNAME ":" CNAME "=" expr` |
| Module4 type dispatch | ✓ | Add `"list"` branch |
| Module5 `ghost_type` IR field | ✓ | Same field |
| Module6 ghost emit dispatcher | ✓ | Add `"list"` branch alongside `"array"` and `"string"` |
| Preamble `use` declarations | ✗ | Lists use `list.List`, `list.Length`, etc. (different from `array.Array`) |

---

## Why3 `list` Module Reference

| Module | Provides |
|--------|---------|
| `list.List` | `type list 'a = Nil \| Cons 'a (list 'a)` |
| `list.Length` | `function length (l: list 'a) : int` |
| `list.Nth` | `function nth (n: int) (l: list 'a) : option 'a` |
| `list.NthNoOpt` | `function nth (n: int) (l: list 'a) : 'a` (partial) |
| `list.Mem` | `predicate mem (x: 'a) (l: list 'a)` |
| `list.Append` | `function (++) (l1 l2: list 'a) : list 'a` |
| `list.Reverse` | `function reverse (l: list 'a) : list 'a` |
| `list.HdTl` | `function hd (l: list 'a) : 'a`, `function tl ...` |
| `list.Permut` | `predicate permut (l1 l2: list 'a)` |
| `list.NumOcc` | `function num_occ (x: 'a) (l: list 'a) : int` |
| `list.SortedInt` | `predicate sorted (l: list int)` |

All are part of Why3's standard library and available with a `use`
declaration.

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| SMT timeout on list induction lemmas | Medium | Why3 list lemmas are well-optimized; keep lists short in tests |
| `\nth` partiality (index out of bounds) | Medium | Use `match ... None -> 0` as safe default; add precondition guidance |
| Confusion between Python `list` (→ `array int`) and ghost `list` (→ `list int`) | High | Use distinct scope type `"ghost_list"` in Module4; document clearly |
| `\append` (snoc) is O(n) in Why3 | Low | Ghost operations are erased — no runtime cost; SMT handles it |
| Interaction with `\old` | Low | `\old(!log)` works naturally for ref-wrapped ghosts |
| Backward compatibility | Low | Default `declared_type="int"` preserves all existing code |

---

## Impact on Verification Capabilities

### Before (current)

- Can prove `\is_sorted(arr, 0, n)` — output is sorted
- Cannot prove "output is a permutation of input" (no snapshot)
- Cannot express "the function processes events in order"
- Cannot express "the output is exactly [1, 2, 3]"

### After (with ghost lists + ghost arrays)

```python
# Prove exact output sequence
#@ ghost expected : list = \cons(1, \cons(2, \cons(3, \nil)))
#@ ensures log == expected

# Prove event ordering
#@ ensures \nth(trace, 0) == init_event
#@ ensures \nth(trace, \list_length(trace) - 1) == final_event

# Prove permutation via list conversion
#@ ghost original : list = \to_list(arr, 0, n)
#@ ensures \is_permutation_list(\to_list(arr, 0, n), original)
```

### Comparison with other tools

| Tool | Ghost lists | List operations | Permutation |
|------|:----------:|:---------------:|:-----------:|
| Frama-C/ACSL | ✗ (uses `\list` logic type, limited) | Limited | Via `\numof` |
| Dafny | ✓ (`ghost var s: seq<int>`) | Full (`.+`, `\|s\|`, `s[i]`) | `multiset(a) == multiset(b)` |
| Why3 | ✓ (`list int`) | Full (`Cons`, `++`, `length`, `nth`, `mem`) | `list.Permut` |
| VeriFast | ✗ (separation logic) | N/A | N/A |
| **PyCSL (current)** | **✗** | **✗** | **✗** |
| **PyCSL (after)** | **✓** | **✓** | **✓** |

---

## Estimated Scope

| Phase | Files changed | Complexity |
|-------|:---:|---|
| 1. Grammar & AST | 1 | Medium — 10 new expression nodes + nil/cons/append/concat/etc. grammar rules |
| 2. Weaver | 0 | None |
| 3. Semantic analysis | 1 | Small — type dispatch + validation |
| 4. IR emission | 1 | Medium — 10 IR handlers |
| 5. Transpiler | 1 | Medium — ghost list emit, 10 expression handlers, preamble imports |
| 6. Conversion builtins | 1 | Medium — `\to_list` logic function, `\sorted_list` predicate |
| 7. Worked example | 0 | Documentation only |
| 8. Tests | 3–4 | Medium — parser + 3 end-to-end reference tests |
| 9. Documentation | 2–3 | Small — skill updates |

### Total new expression nodes: 10

`\nil`, `\cons`, `\append`, `\concat`, `\list_length`, `\nth`,
`\mem`, `\reverse`, `\hd`, `\tl`

Plus 3 optional conversion/predicate builtins:
`\to_list`, `\sorted_list`, `\is_permutation_list`
