# Ghost Tuple Variables — Implementation Plan

## Problem Statement

PyCSL ghost variables are currently **integer-only**. Ghost tuples
would let contracts track multiple related values as a single logical
unit — return value decomposition, coordinate pairs, key-value
witnesses, and state snapshots with named components.

### Why tuples?

Tuples differ from the other ghost types (arrays, lists, strings) in
that they are **fixed-arity, heterogeneous-in-principle** (though
PyCSL maps all elements to `int`), and **immutable**. They serve as
lightweight product types for grouping specification values.

| | Ghost scalar | Ghost tuple | Ghost array | Ghost list |
|---|---|---|---|---|
| Why3 type | `ref int` | `ref (int, int, ...)` | `array int` | `ref (list int)` |
| Arity | 1 | Fixed N ≥ 2 | Variable | Variable |
| Mutable | Ref-assign | Ref-assign (whole) | In-place | Ref-assign |
| Access | `!x` | `let (a,b) = !t in a` | `a.(i)` | `match !l with...` |

### Motivating examples

**1. Snapshot a pair of values:**

```python
#@ ghost old_bounds : tuple2 = \mktuple(lo, hi)
# ... modify lo and hi ...
#@ ensures lo <= \fst(old_bounds)
#@ ensures hi >= \snd(old_bounds)
```

**2. Track function return decomposition:**

```python
#@ ghost result_pair : tuple2 = \mktuple(quotient, remainder)
#@ ensures \fst(result_pair) * divisor + \snd(result_pair) == dividend
```

**3. Ghost pair in loop invariant (two-pointer):**

```python
while left < right:
    #@ loop invariant \fst(bounds) <= left
    #@ loop invariant right <= \snd(bounds)
    #@ ghost bounds = \mktuple(left, right)
    ...
```

### Target syntax

```python
#@ ghost p : tuple2 = \mktuple(a, b)          # pair
#@ ghost t : tuple3 = \mktuple(a, b, c)       # triple
#@ ensures \fst(p) == a                        # first component
#@ ensures \snd(p) == b                        # second component
#@ ensures \proj(t, 0) == a                    # nth projection (0-based)
#@ ensures \proj(t, 1) == b
#@ ensures \proj(t, 2) == c
#@ ghost p = \mktuple(new_a, new_b)            # whole-tuple reassignment
```

### Why3 target

```why3
let ghost p = ref (a, b) in
let ghost t = ref (a, b, c) in
assert { let (x, _) = !p in x = a };           (* fst *)
assert { let (_, y) = !p in y = b };           (* snd *)
assert { let (_, _, z) = !t in z = c };        (* proj 2 *)
ghost p := (new_a, new_b);                      (* reassign *)
```

---

## Current State (per module)

| Module | Tuple support today | Ghost support today |
|--------|-------------------|-------------------|
| **Module2** (Parser) | `\result[i]` parses for tuple returns | Ghost: untyped, int only |
| **Module4** (Semantic) | Tuple return type tracked via `find_return_type` | Ghost: hard-coded `int` |
| **Module5** (IR Emitter) | `{"type":"Tuple", "elts":[...]}` in expressions | Ghost IR: no type field |
| **Module6** (Transpiler) | Tuple literals → `(e1, e2, ...)`, `TupleUnpack` → `let (a,b) = ...`, `\result[i]` → let-destructure | Ghost: `ref int` only; **tuple values → `0`** in assign context |

The critical current limitation is at line 1377–1379 of Module6:

```python
# Tuple/Set literals can't be stored in int refs; use 0 as placeholder
if vt in ("Tuple", "SetLit"):
    val = "0"
```

Tuple values are **discarded** in assignment context because there's
no `ref (int, int)` path. Ghost tuples would provide exactly that.

---

## Design Decisions

### D1. Fixed arity types: `tuple2`, `tuple3`, `tuple4`

Rather than a single polymorphic `tuple` type (which would require
arity inference), use explicit arity declarations:

```python
#@ ghost p : tuple2 = \mktuple(a, b)
#@ ghost t : tuple3 = \mktuple(x, y, z)
#@ ghost q : tuple4 = \mktuple(a, b, c, d)
```

**Rationale**: Why3 tuples are structural product types — `(int, int)`
and `(int, int, int)` are completely different types. The arity must
be known at emit time. Explicit declaration avoids fragile inference.

Support arities 2–4 initially (covers 95%+ of use cases). Higher
arities can be added trivially.

### D2. Storage model: ref-wrapped

Ghost tuples are ref-wrapped (`ref (int, int)`). Like ghost scalars
and ghost lists, tuple values are immutable — modification is
whole-tuple reassignment:

```why3
let ghost p = ref (a, b) in
ghost p := (new_a, new_b);     (* whole-tuple reassign *)
assert { let (x, _) = !p in x = new_a }
```

### D3. Access via `\fst`, `\snd`, `\proj`

- `\fst(t)` — first component (arity ≥ 2)
- `\snd(t)` — second component (arity ≥ 2)
- `\proj(t, i)` — ith component (0-based, arity ≥ i+1)

All three emit let-destructure patterns in Why3:

```why3
(* \fst(p) where p is a ref (int, int) *)
(let (_v0, _) = !p in _v0)

(* \proj(t, 2) where t is a ref (int, int, int) *)
(let (_, _, _v2) = !t in _v2)
```

### D4. No element-wise mutation

Ghost tuples support only whole-tuple reassignment, not
component-level mutation. This keeps the type model simple and
avoids needing WhyML record mutation syntax.

To update one component:
```python
#@ ghost p = \mktuple(new_x, \snd(p))   # update first, keep second
```

### D5. Augmented assignments

`+=`, `-=`, `*=` are **rejected** for tuple ghosts. Only `=` is
allowed.

---

## Implementation Plan

### Phase 1 — Grammar & AST (Module2)

**File: `src/pycsl/Module2_Parser.py`**

1. Extend `GhostAssignDecl` (shared with string/array/list):

```python
@dataclass
class GhostAssignDecl(CSLNode):
    target: str
    value: CSLNode
    op: str            # "=" only for tuples
    declared_type: str  # "int", "string", "array", "list",
                        # "tuple2", "tuple3", "tuple4"
```

2. Grammar rules for typed ghost declaration (shared rule):

```lark
ghost_assign: "ghost" CNAME "=" expr
            | "ghost" CNAME ":" CNAME "=" expr
            | "ghost" CNAME ":" CNAME NUMBER "=" expr
```

The third alternative handles `ghost p : tuple2 = ...` where `tuple`
is the CNAME and `2` is a NUMBER suffix. Alternatively, treat
`tuple2`, `tuple3`, `tuple4` as single tokens:

```lark
ghost_assign: "ghost" CNAME "=" expr
            | "ghost" CNAME ":" GHOST_TYPE "=" expr

GHOST_TYPE: "int" | "string" | "array" | "list"
          | "tuple2" | "tuple3" | "tuple4"
```

3. Add built-in expression nodes for tuple operations:

```lark
| "\\mktuple" "(" expr_list ")" -> mktuple_expr
| "\\fst" "(" expr ")" -> fst_expr
| "\\snd" "(" expr ")" -> snd_expr
| "\\proj" "(" expr "," expr ")" -> proj_expr
```

4. AST nodes:

```python
@dataclass
class MkTupleExpr(CSLNode):
    """Construct a ghost tuple: \\mktuple(a, b) or \\mktuple(a, b, c)."""
    elts: list    # list of CSLNode

@dataclass
class FstExpr(CSLNode):
    """First component: \\fst(t)."""
    tuple_expr: CSLNode

@dataclass
class SndExpr(CSLNode):
    """Second component: \\snd(t)."""
    tuple_expr: CSLNode

@dataclass
class ProjExpr(CSLNode):
    """Nth projection: \\proj(t, i)."""
    tuple_expr: CSLNode
    index: CSLNode
```

### Phase 2 — Weaver (Module3)

No change needed — `GhostAssignDecl` pass-through is type-agnostic.

### Phase 3 — Semantic analysis (Module4)

**File: `src/pycsl/Module4_SemanticAnalyzer.py`**

1. Register ghost tuples in scope:

```python
ghost_type = getattr(ga, 'declared_type', 'int')
if ghost_type.startswith("tuple"):
    arity = int(ghost_type[-1])  # "tuple2" → 2
    self.current_scope[ga.target] = f"ghost_tuple{arity}"
```

2. Validation:
   - `\mktuple` arity must match declared arity
   - `\fst`, `\snd` require arity ≥ 2
   - `\proj(t, i)` requires `i` < declared arity (when `i` is a
     literal)
   - `+=`, `-=`, `*=` → error for tuple ghosts

### Phase 4 — IR emission (Module5)

**File: `src/pycsl/Module5_IREmitter.py`**

1. Carry type through IR (shared infrastructure):

```python
ir_stmts.append({
    "stmt": "GhostAssign",
    "target": ga.target,
    "value": self._csl_to_ir(ga.value),
    "op": ga.op,
    "ghost_type": getattr(ga, 'declared_type', 'int'),
})
```

2. Add IR handlers:

```python
def _csl_mktuple(self, node: MkTupleExpr) -> Dict[str, Any]:
    return {"type": "MkTuple",
            "elts": [self._csl_to_ir(e) for e in node.elts]}

def _csl_fst(self, node: FstExpr) -> Dict[str, Any]:
    return {"type": "TupleFst",
            "tuple": self._csl_to_ir(node.tuple_expr)}

def _csl_snd(self, node: SndExpr) -> Dict[str, Any]:
    return {"type": "TupleSnd",
            "tuple": self._csl_to_ir(node.tuple_expr)}

def _csl_proj(self, node: ProjExpr) -> Dict[str, Any]:
    return {"type": "TupleProj",
            "tuple": self._csl_to_ir(node.tuple_expr),
            "index": self._csl_to_ir(node.index)}
```

### Phase 5 — WhyML transpiler (Module6)

**File: `src/pycsl/Module6_WhyMLTranspiler.py`**

#### 5a. Ghost tuple declaration

In `_handle_ghost_assign_stmt`:

```python
if ghost_type.startswith("tuple"):
    arity = int(ghost_type[-1])
    self._ghost_tuple_vars[target] = arity

    if target not in declared_refs:
        declared_refs.add(target)
        local_refs.add(target)
        rest_code = self._stmts_to_whyml(rest, ...)
        if not rest_code:
            rest_code = f"{indent}()"

        val_ir = stmt.get("value", {})
        if val_ir.get("type") == "MkTuple":
            elts = [self._expr_to_whyml(e, local_refs)
                    for e in val_ir["elts"]]
            tuple_val = f"({', '.join(elts)})"
        else:
            tuple_val = self._expr_to_whyml(stmt["value"], local_refs)

        tuple_type = ", ".join(["int"] * arity)
        return (f"{indent}let ghost {safe_target} = "
                f"ref ({tuple_val} : ({tuple_type})) in\n"
                f"{rest_code}")

    # Reassignment (whole-tuple only)
    val_ir = stmt.get("value", {})
    if val_ir.get("type") == "MkTuple":
        elts = [self._expr_to_whyml(e, local_refs)
                for e in val_ir["elts"]]
        tuple_val = f"({', '.join(elts)})"
    else:
        tuple_val = self._expr_to_whyml(stmt["value"], local_refs)
    code = f"{indent}ghost {safe_target} := {tuple_val}"
    if rest:
        code += ";\n" + self._stmts_to_whyml(rest, ...)
    return code
```

#### 5b. Tuple expression handlers

Add to `_expr_to_whyml` dispatch:

```python
if t == "MkTuple":
    elts = [self._expr_to_whyml(e, local_refs, invariant_ctx, subst)
            for e in ir_expr["elts"]]
    return f"({', '.join(elts)})"

if t == "TupleFst":
    tup = self._expr_to_whyml(ir_expr["tuple"], local_refs, ...)
    arity = self._get_ghost_tuple_arity(ir_expr["tuple"])
    wildcards = ", ".join(["_"] * (arity - 1))
    return f"(let (_v0, {wildcards}) = {tup} in _v0)"

if t == "TupleSnd":
    tup = self._expr_to_whyml(ir_expr["tuple"], local_refs, ...)
    arity = self._get_ghost_tuple_arity(ir_expr["tuple"])
    rest = ", ".join(["_"] * (arity - 2)) if arity > 2 else ""
    pattern = f"_, _v1" + (f", {rest}" if rest else "")
    return f"(let ({pattern}) = {tup} in _v1)"

if t == "TupleProj":
    tup = self._expr_to_whyml(ir_expr["tuple"], local_refs, ...)
    idx_expr = ir_expr["index"]
    try:
        idx = int(idx_expr.get("value", -1))
    except (TypeError, ValueError):
        idx = -1
    arity = self._get_ghost_tuple_arity(ir_expr["tuple"])
    if 0 <= idx < arity:
        parts = ["_"] * arity
        parts[idx] = f"_v{idx}"
        pattern = ", ".join(parts)
        return f"(let ({pattern}) = {tup} in _v{idx})"
    # Fallback for dynamic index — not supported, emit 0
    return "0"
```

Helper to look up arity:

```python
def _get_ghost_tuple_arity(self, ir_expr):
    """Resolve the arity of a ghost tuple expression."""
    if ir_expr.get("type") == "Var":
        name = ir_expr.get("name", "")
        return self._ghost_tuple_vars.get(name, 2)
    return 2  # default pair
```

#### 5c. Ghost tuple variable tracking

1. Add `self._ghost_tuple_vars: Dict[str, int] = {}` to
   `_reset_function_state` (maps name → arity).

2. Ghost tuple variables use `!` dereference (ref-wrapped). They
   are in `local_refs` after declaration, so the existing Var
   handler already emits `!`.

3. Exclude from parameter lists (same as other ghost vars).

#### 5d. Reading ghost tuples in contracts

When `\fst(p)` or `\snd(p)` appears in `ensures`/`loop invariant`,
the ghost tuple variable `p` must be dereffed with `!`:

```why3
ensures { let (x, _) = !p in x = a }
```

The Var handler already emits `!p` for variables in `local_refs`.
The let-destructure around it comes from the `TupleFst`/`TupleSnd`
handler.

---

### Phase 6 — Tests

1. **Parser test**: verify `\mktuple(a, b)`, `\fst(p)`, `\snd(p)`,
   `\proj(t, 2)` all parse correctly.

2. **End-to-end reference test — pair snapshot:**

```python
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == a + b
#@ assigns \nothing
def sum_pair(a: int, b: int) -> int:
    #@ ghost p : tuple2 = \mktuple(a, b)
    result: int = a + b
    #@ assert result == \fst(p) + \snd(p)
    return result
```

3. **End-to-end reference test — triple with projection:**

```python
#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def triple_test(x: int, y: int, z: int) -> int:
    #@ ghost t : tuple3 = \mktuple(x, y, z)
    #@ assert \proj(t, 0) == x
    #@ assert \proj(t, 1) == y
    #@ assert \proj(t, 2) == z
    return x + y + z
```

4. **Reassignment test:**

```python
#@ requires lo < hi
#@ ensures \result == hi - lo
#@ assigns \nothing
def range_size(lo: int, hi: int) -> int:
    #@ ghost bounds : tuple2 = \mktuple(lo, hi)
    #@ ghost bounds = \mktuple(lo + 1, hi - 1)
    result: int = hi - lo
    return result
```

### Phase 7 — Documentation

1. Update `config/skills/pycsl-annotate/SKILL.md`:
   - Add `tuple2`, `tuple3`, `tuple4` ghost types
   - Add `\mktuple`, `\fst`, `\snd`, `\proj` to expression reference

2. Update `config/skills/contract-writer/SKILL.md`:
   - Add tuple ghost types to allowed types
   - Document tuple access patterns

3. Update `config/skills/invariant-writer/SKILL.md`:
   - Ghost tuples in loop invariants (e.g., tracking two-pointer
     bounds)

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
Phase 6 (Tests)
    ↓
Phase 7 (Documentation)
```

### Shared infrastructure with string/array/list ghost plans

| Component | Shared? |
|-----------|:-------:|
| `declared_type` field on `GhostAssignDecl` | ✓ |
| `GHOST_TYPE` terminal in grammar | ✓ (add `tuple2` \| `tuple3` \| `tuple4`) |
| Module4 type dispatch | ✓ (add `tuple*` branch) |
| Module5 `ghost_type` IR field | ✓ |
| Module6 ghost emit dispatcher | ✓ (add `tuple*` branch) |

---

## Why3 Tuple Semantics Reference

Why3 tuples are structural products:

```why3
(* Construction *)
let p = (1, 2) in             (* type: (int, int) *)
let t = (1, 2, 3) in          (* type: (int, int, int) *)

(* Destructuring — the ONLY access method *)
let (a, b) = p in a           (* first component *)
let (_, b) = p in b           (* second component *)
let (_, _, c) = t in c        (* third component *)

(* Ghost tuples *)
let ghost p = ref (0, 0) in
ghost p := (1, 2);
assert { let (x, _) = !p in x = 1 }
```

There is no `fst`/`snd` function in Why3 stdlib — access is always
via pattern matching or let-destructure. PyCSL's `\fst`/`\snd`/`\proj`
are syntactic sugar that emit let-destructure patterns.

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| `\proj` with non-literal index | Medium | Reject at semantic analysis; only literal indices 0..N-1 |
| Arity mismatch (`tuple2` with 3 elements) | Medium | Validate at Module4; error if `\mktuple` arity ≠ declared arity |
| Deep nesting of `let (...) = !t in ...` | Low | Why3 handles this well; SMT solvers excel at equality reasoning |
| Interaction with `\old` | Low | `\old(!p)` works for ref-wrapped ghosts (Why3 snapshots the ref) |
| Backward compatibility | None | No existing code uses ghost tuples |

---

## Comparison with Other Tools

| Tool | Ghost tuples | Access | Construction |
|------|:-----------:|:------:|:------------:|
| Frama-C/ACSL | ✗ (use ghost struct) | N/A | N/A |
| Dafny | ✓ (`ghost var p: (int,int)`) | `p.0`, `p.1` | `(a, b)` |
| Why3 | ✓ (`let ghost p = ref (a,b)`) | `let (x,_) = !p in x` | `(a, b)` |
| Viper | ✗ | N/A | N/A |
| **PyCSL (current)** | **✗** | **✗** | **✗** |
| **PyCSL (after)** | **✓** | `\fst`, `\snd`, `\proj` | `\mktuple(...)` |

---

## Estimated Scope

| Phase | Files changed | Complexity |
|-------|:---:|---|
| 1. Grammar & AST | 1 | Small — 4 expression nodes + grammar rules |
| 2. Weaver | 0 | None |
| 3. Semantic analysis | 1 | Small — arity validation |
| 4. IR emission | 1 | Small — 4 IR handlers |
| 5. Transpiler | 1 | Medium — ghost tuple declaration, 4 expression handlers, arity tracking |
| 6. Tests | 2–3 | Small — parser + 3 end-to-end tests |
| 7. Documentation | 2–3 | Small — skill updates |

Ghost tuples are the **simplest** of the four ghost-type extensions
(string, array, list, tuple) because:
- No new Why3 imports needed (tuples are built-in)
- No recursive data structure concerns
- No element mutation path
- Small fixed number of operations (`\mktuple`, `\fst`, `\snd`, `\proj`)
