# Ghost String Variables — Implementation Plan

## Problem Statement

PyCSL ghost variables are currently **integer-only**. This limitation
prevents Layer 1 contracts from expressing properties about string
outputs — the "string-building barrier" described in `gen-contract.md`.

If ghost variables could hold strings and contracts could reason about
string concatenation, the Layer 3 bridge (`pycsl-wp-spec.mlw`) could be
partially or fully eliminated for WP arms whose output is a simple
concatenation.

### Target syntax

```python
#@ ghost s : string = "let "
#@ ghost s = s ^ lhs ^ " := " ^ rhs_str ^ ";\n"
#@ ensures \result == s
```

### Why3 target

```why3
let ghost s = ref "let " in
ghost s := String.(^) !s (String.(^) lhs (String.(^) " := " (String.(^) rhs_str ";\n")));
assert { result = !s }
```

---

## Current State (per module)

| Module | Ghost handling | String handling | Hard-coded `int` |
|--------|--------------|-----------------|:---:|
| **Module2** (Parser) | `ghost CNAME "=" expr` — untyped | `ESCAPED_STRING → StringLiteral` (already parsed) | — |
| **Module3** (Weaver) | Passes `GhostAssignDecl` through to AST | No type info | — |
| **Module4** (SemanticAnalyzer) | `self.current_scope[ga.target] = "int"` | — | ✓ |
| **Module5** (IR Emitter) | `{"stmt":"GhostAssign", "target":…, "value":…, "op":…}` — no type field | `{"type":"String", "value":"…"}` for contract expr | — |
| **Module6** (Transpiler) | `let ghost x = ref (val : int) in` | Strings → `hash(s) % 2^31` in body context; preserved as `"…"` in spec context | ✓ |

Key insight: **strings already parse** as expressions (`ESCAPED_STRING` →
`StringLiteral` → `{"type":"String"}`). The problem is downstream:
Module4 forces `int` scope, Module6 hashes strings to ints in body
context, and the ghost emit code forces `ref int`.

---

## Implementation Plan

### Phase 1 — Grammar & AST (Module2)

**File: `src/pycsl/Module2_Parser.py`**

1. Extend `GhostAssignDecl` to carry an optional type annotation:

```python
@dataclass
class GhostAssignDecl(CSLNode):
    target: str
    value: CSLNode
    op: str            # "=" or "+=" or "-=" or "*="
    declared_type: str  # "int" (default) or "string"
```

2. Add a new grammar rule for typed ghost declarations:

```lark
ghost_assign: "ghost" CNAME "=" expr
            | "ghost" CNAME ":" CNAME "=" expr
```

The second alternative captures `ghost s : string = "hello"`.

3. Update the Lark transformer to populate `declared_type`:

```python
def ghost_assign(self, items):
    if len(items) == 3:  # typed: ghost name : type = expr
        return GhostAssignDecl(target=str(items[0]),
                               value=items[2], op="=",
                               declared_type=str(items[1]))
    return GhostAssignDecl(target=str(items[0]),
                           value=items[1], op="=",
                           declared_type="int")
```

4. Define the string concatenation operator `^` in the expression grammar:

```lark
?term: factor | term ADD_OP factor | term "^" factor -> str_concat_expr
```

And the AST node:

```python
@dataclass
class StrConcatExpr(CSLNode):
    left: CSLNode
    right: CSLNode
```

**Backward compatibility**: existing `ghost x = expr` is unchanged (defaults to `declared_type="int"`).

### Phase 2 — Weaver pass-through (Module3)

**File: `src/pycsl/Module3_Weaver.py`**

Minimal change: the weaver attaches `GhostAssignDecl` objects to AST
nodes unchanged. Since `declared_type` is a new field on the existing
dataclass, the weaver code is already compatible — no modifications
needed unless filtering logic inspects fields.

Verify: `isinstance(c, GhostAssignDecl)` checks still pass.

### Phase 3 — Semantic analysis (Module4)

**File: `src/pycsl/Module4_SemanticAnalyzer.py`**

1. Use declared type instead of hard-coded `"int"`:

```python
# Before
self.current_scope[ga.target] = "int"

# After
ghost_type = getattr(ga, 'declared_type', 'int')
self.current_scope[ga.target] = "str" if ghost_type == "string" else "int"
```

2. Add type-checking for ghost augmented assignments:
   - `string` ghosts: allow `=` only (or `= s ^ expr` for concat).
     Reject `+=`, `-=`, `*=` on string ghosts.
   - `int` ghosts: current behavior unchanged.

3. Validate that string ghost values are string-typed expressions
   (or variables known to be strings).

### Phase 4 — IR emission (Module5)

**File: `src/pycsl/Module5_IREmitter.py`**

1. Carry the type through to IR:

```python
for ga in getattr(stmt, 'csl_ghost_assigns', []):
    ir_stmts.append({
        "stmt": "GhostAssign",
        "target": ga.target,
        "value": self._csl_to_ir(ga.value),
        "op": ga.op,
        "ghost_type": getattr(ga, 'declared_type', 'int'),
    })
```

2. Add IR handler for `StrConcatExpr`:

```python
def _csl_str_concat(self, node: StrConcatExpr) -> Dict[str, Any]:
    return {
        "type": "StrConcat",
        "left": self._csl_to_ir(node.left),
        "right": self._csl_to_ir(node.right),
    }
```

Register in the dispatch table:

```python
StrConcatExpr: "_csl_str_concat",
```

### Phase 5 — WhyML transpiler (Module6)

**File: `src/pycsl/Module6_WhyMLTranspiler.py`**

This is the most substantial change. Five sub-tasks:

#### 5a. Ghost declaration emit

In `_handle_ghost_assign_stmt` (~line 1683):

```python
def _handle_ghost_assign_stmt(self, stmt, rest, local_refs,
                               declared_refs, indent, in_loop):
    target = stmt["target"]
    safe_target = self._whyml_ident(target)
    op = stmt.get("op", "=")
    ghost_type = stmt.get("ghost_type", "int")
    val = self._expr_to_whyml(stmt["value"], local_refs | {target})

    if target not in declared_refs:
        declared_refs.add(target)
        local_refs.add(target)
        rest_code = self._stmts_to_whyml(rest, local_refs,
                                          declared_refs, indent, in_loop)
        if not rest_code:
            rest_code = f"{indent}()"

        if ghost_type == "string":
            # Don't hash — preserve string literal
            str_val = self._expr_to_whyml_string_ctx(stmt["value"], local_refs)
            return (f"{indent}let ghost {safe_target} = ref {str_val} in\n"
                    f"{rest_code}")
        else:
            # Existing int path
            if self._bounded_int:
                return (f"{indent}let ghost {safe_target} = "
                        f"ref ({val} : int{self._bounded_int}) in\n"
                        f"{rest_code}")
            return (f"{indent}let ghost {safe_target} = ref {val} in\n"
                    f"{rest_code}")

    # Reassignment
    if ghost_type == "string":
        str_val = self._expr_to_whyml_string_ctx(stmt["value"], local_refs)
        code = f"{indent}ghost {safe_target} := {str_val}"
    elif op == "=":
        code = f"{indent}ghost {safe_target} := {val}"
    elif op == "+=":
        code = f"{indent}ghost {safe_target} := !{safe_target} + {val}"
    # ... existing -= *= ...
```

#### 5b. String expression transpiler

Add a new method that transpiles expressions preserving string
semantics (no hashing):

```python
def _expr_to_whyml_string_ctx(self, ir_expr, local_refs):
    """Transpile an expression in string context — no int hashing."""
    if not ir_expr:
        return '""'
    t = ir_expr.get("type", "")
    if t == "String":
        escaped = ir_expr["value"].replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    if t == "StrConcat":
        left = self._expr_to_whyml_string_ctx(ir_expr["left"], local_refs)
        right = self._expr_to_whyml_string_ctx(ir_expr["right"], local_refs)
        return f"(String.(^) {left} {right})"
    if t == "Var":
        name = ir_expr.get("name", "")
        safe = self._whyml_ident(name)
        if name in local_refs:
            return f"!{safe}"
        return safe
    # Fallback: coerce int to string via abstract op
    int_val = self._expr_to_whyml(ir_expr, local_refs)
    self._add_abstract_op("val int_to_string (x: int) : string")
    return f"(int_to_string {int_val})"
```

#### 5c. String expressions in contracts

In `_expr_to_whyml` (~line 1290), when `_in_spec` is True and the
expression is a `String`, preserve it instead of hashing:

```python
if t == "String":
    escaped = ir_expr["value"].replace('\\', '\\\\').replace('"', '\\"')
    if getattr(self, '_in_spec', False):
        return f'"{escaped}"'        # ← preserve in contracts
    return str(hash(f'"{escaped}"') % 2147483647)  # ← hash in body
```

And add the `StrConcat` handler:

```python
if t == "StrConcat":
    left = self._expr_to_whyml(ir_expr["left"], local_refs, invariant_ctx, subst)
    right = self._expr_to_whyml(ir_expr["right"], local_refs, invariant_ctx, subst)
    self._needs_string = True
    return f"(String.(^) {left} {right})"
```

#### 5d. Track ghost types

Extend `IRScanner.find_ghost_vars` to return type info, or maintain
a `_ghost_types: Dict[str, str]` map in the transpiler. When emitting
parameters, skip string ghosts from the int parameter list.

#### 5e. Auto-import `string.String`

If any ghost is string-typed, ensure `use string.String` is emitted
in the preamble (the flag `needs["needs_string"]` already controls this
at line 2408 — extend it to detect string ghost usage).

### Phase 6 — Contract builtins

Add `\str_length(s)` and `\str_sub(s, lo, hi)` as built-in contract
functions mapping to Why3's `String.length` and `String.sub`:

**Module2 grammar:**
```lark
| "\\str_length" "(" CNAME ")" -> str_length_expr
| "\\str_sub" "(" CNAME "," expr "," expr ")" -> str_sub_expr
```

**Module6 emit:**
```python
if t == "StrLength":
    return f"(String.length {self._whyml_ident(ir_expr['name'])})"
```

These are optional for Phase 1 but needed to express non-trivial
string properties (e.g., `ensures \str_length(\result) > 0`).

### Phase 7 — Tests

1. **Parser test**: `#@ ghost s : string = "hello"` parses to
   `GhostAssignDecl(target="s", declared_type="string", …)`

2. **IR test**: ghost IR carries `"ghost_type": "string"`

3. **End-to-end reference test** (`test-suite/corpus/pycsl-reference/`):

```python
#@ requires 1 == 1
#@ ensures \result == "ab"
#@ assigns \nothing
def concat_test() -> str:
    #@ ghost s : string = "a"
    #@ ghost s = s ^ "b"
    return "ab"
```

4. **Self-annotation test**: annotate one Module6 handler using string
   ghosts to verify the string-building barrier is closed at Layer 1.

### Phase 8 — Documentation

1. Update `config/skills/pycsl-annotate/SKILL.md` — add string ghost
   syntax to the annotation reference.
2. Update `config/skills/contract-writer/SKILL.md` — add `^` operator,
   `\str_length`, `\str_sub` to the allowed-expressions list.
3. Update `gen-contract.md` — note that the string-building barrier
   can now be partially closed at Layer 1.

---

## Dependency Graph

```
Phase 1 (Grammar)
    ↓
Phase 2 (Weaver) ← trivial, just verify
    ↓
Phase 3 (Semantic analysis)
    ↓
Phase 4 (IR emission)
    ↓
Phase 5 (Transpiler) ← largest change
    ↓
Phase 6 (Contract builtins) ← optional, can defer
    ↓
Phase 7 (Tests)
    ↓
Phase 8 (Documentation)
```

Phases 1–5 are the critical path. Phase 6 is optional but valuable.
Phases 7–8 should track the implementation.

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| SMT solver timeout on string concatenation | Medium | Z3's string theory is mature; CVC5 even better. Benchmark with 5-concat chains |
| Backward compatibility | Low | Default `declared_type="int"` preserves all existing tests |
| Self-referential bootstrap | Medium | Changes modify Module2 (the contract parser) — re-verify after implementation |
| Why3 `string.String` expressiveness | Low | Only need `(^)`, `length`, `sub`, `=` — all available in Why3 stdlib |
| `^` conflicts with existing syntax | Low | `^` is not currently used in the contract grammar; Python uses `^` for XOR but PyCSL contracts don't support bitwise ops |

---

## Impact on the String-Building Barrier

With string ghosts, the Layer 1 annotation for `_handle_assign_stmt`
could become:

```python
#@ ghost _out : string = ""
#@ ensures \result == _out
#@ assigns self._abstract_ops
def _handle_assign_stmt(self, stmt, rest_str, indent, ...):
    ...
    if target not in declared_refs:
        #@ ghost _out = indent ^ "let " ^ lhs ^ " = ref " ^ rhs_str ^ " in\n" ^ rest_str
        return f"{indent}let {lhs} = ref {rhs_str} in\n{rest_str}"
    else:
        #@ ghost _out = indent ^ lhs ^ " := " ^ rhs_str ^ ";\n" ^ rest_str
        return f"{indent}{lhs} := {rhs_str};\n{rest_str}"
```

This **eliminates the need for Layer 3 val specs** for this arm.
Applied across all 10 WP arms, it could replace:
- 10 `val` string specs
- 9 `val function` code specs
- 4 human-audited coherence axioms

with machine-checked Layer 1 + Layer 2 proofs alone.

---

## Estimated Scope

| Phase | Files changed | Complexity |
|-------|:---:|---|
| 1. Grammar & AST | 1 | Small — 2 grammar rules + 1 field |
| 2. Weaver | 0–1 | Trivial — verify only |
| 3. Semantic analysis | 1 | Small — 1 conditional |
| 4. IR emission | 1 | Small — 1 field + 1 handler |
| 5. Transpiler | 1 | Medium — new method + branch in ghost handler + StrConcat handler |
| 6. Contract builtins | 2 | Small — 2 grammar rules + 2 emit branches |
| 7. Tests | 2–3 | Small — reference test + parser test |
| 8. Documentation | 2–3 | Small — skill updates |
