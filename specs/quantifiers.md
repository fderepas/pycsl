# Plan: `\forall` and `\exists` Quantifier Keywords

## Current State

Both `\forall` and `\exists` (with an **s**) are **already fully implemented**
across the entire pipeline:

| Module | Status | Details |
|--------|--------|---------|
| Module2\_Parser.py | ✅ Done | AST nodes `Forall`/`Exists` (lines 80–87), grammar rules (lines 173–174), transformer methods (lines 244–245) |
| Module3\_Weaver.py | ✅ Done | Handled dynamically via generic weaving logic |
| Module4\_SemanticAnalyzer.py | ✅ Done | Variable extraction excludes bound var, scope validation (lines 43–45, 133–134) |
| Module5\_IREmitter.py | ✅ Done | Converts to `{"type": "Forall"/"Exists", "var": ..., "body": ...}` (lines 42–45) |
| Module6\_WhyMLTranspiler.py | ✅ Done | Emits `(forall x : int. ...)` / `(exists x : int. ...)` (lines 236–244) |

### What is missing

1. **`\exist` (singular, no 's')** is **NOT** accepted — only `\exists` works.
   The user asked for `\exist`, which is currently a parse error.

2. **Quantifiers cannot appear as the right-hand operand of any binary
   operator** (`==>`, `and`, `or`, etc.) unless wrapped in parentheses.
   This is the main grammar limitation addressed by this plan.

---

## Grammar Limitation: Quantifiers Inside Binary Operators

### The problem

The current Lark EBNF grammar (Module2\_Parser.py, lines 171–177) is:

```ebnf
?expr: implication
     | "\\forall" CNAME ";" expr -> forall_expr
     | "\\exists" CNAME ";" expr -> exists_expr

?implication: logical_or | implication IMPL_OP logical_or
?logical_or:  logical_and | logical_or OR_OP logical_and
?logical_and: equality    | logical_and AND_OP equality
```

Quantifiers are alternatives to `implication` at the top `expr` level.
But every binary operator uses a *lower* precedence level on its right-hand
side — `implication` uses `logical_or`, `logical_or` uses `logical_and`, etc.
None of those include quantifiers.

### What works and what doesn't

| Expression | Status | Why |
|---|---|---|
| `\forall i; 0 <= i and i < n ==> arr[i] >= 0` | ✅ works | Quantifier is the top-level `expr` |
| `\exists j; 0 <= j and j < n and arr[j] == target` | ✅ works | Same — top level |
| `found == 0 ==> \forall i; body` | ❌ parse error | RHS of `==>` must be `logical_or`, not `expr` |
| `n > 0 and \forall i; body` | ❌ parse error | RHS of `and` must be `equality`, not `expr` |
| `n > 0 or \exists j; body` | ❌ parse error | RHS of `or` must be `logical_and`, not `expr` |
| `found == 0 ==> (\forall i; body)` | ✅ works | `( expr )` is an `atom`, so quantifiers inside parens are fine |
| `n > 0 and (\forall i; body)` | ✅ works | Same — parenthesized |

**Summary:** quantifiers only parse at the very top of an expression or
inside explicit parentheses.  They cannot appear "bare" as the RHS of `==>`,
`and`, or `or`.

### Why it matters

The most natural specification patterns need bare quantifiers after `==>`:

```python
#@ loop invariant found == 0 ==> \forall k; 0 <= k and k < i ==> arr[k] != target
#@ ensures       sorted == 1 ==> \forall k; 0 <= k and k < n - 1 ==> arr[k] <= arr[k+1]
```

Requiring parentheses is possible (`==> (\forall k; ...)`) but unintuitive
and inconsistent with ACSL / Frama-C, where quantifiers have the lowest
binding power and can appear anywhere without parentheses.

---

## Plan

### Approach: introduce `qexpr` ("quantifiable expression") non-terminals

For each binary operator level whose RHS currently points to a lower
precedence level, add an alternative RHS that also accepts quantifiers.
This lets quantifiers appear bare after any binary operator.

The quantifier body remains `expr` (greedy — consumes everything to the
right), which is the standard semantics in first-order logic and ACSL.

### 1. Grammar change (Module2\_Parser.py, lines 171–178)

**Before:**

```ebnf
?expr: implication
     | "\\forall" CNAME ";" expr -> forall_expr
     | "\\exists" CNAME ";" expr -> exists_expr

?implication: logical_or | implication IMPL_OP logical_or
?logical_or:  logical_and | logical_or OR_OP logical_and
?logical_and: equality    | logical_and AND_OP equality
```

**After:**

```ebnf
?expr: implication
     | "\\forall" CNAME ";" expr -> forall_expr
     | "\\exists" CNAME ";" expr -> exists_expr

?implication: logical_or
            | implication IMPL_OP logical_or
            | implication IMPL_OP "\\forall" CNAME ";" expr -> impl_forall
            | implication IMPL_OP "\\exists" CNAME ";" expr -> impl_exists

?logical_or: logical_and
           | logical_or OR_OP logical_and
           | logical_or OR_OP "\\forall" CNAME ";" expr -> impl_forall
           | logical_or OR_OP "\\exists" CNAME ";" expr -> impl_exists

?logical_and: equality
            | logical_and AND_OP equality
            | logical_and AND_OP "\\forall" CNAME ";" expr -> impl_forall
            | logical_and AND_OP "\\exists" CNAME ";" expr -> impl_exists
```

The `-> impl_forall` / `-> impl_exists` aliases route to new transformer
methods (see next step).

*Note:* An LALR conflict is possible between the existing `implication IMPL_OP
logical_or` and the new `implication IMPL_OP "\\forall" ...`.  Lark's LALR
parser resolves this by lookahead — when the token after `IMPL_OP` is
`\\forall` or `\\exists`, the quantifier alternative is taken; otherwise the
`logical_or` alternative is used.  If Lark reports ambiguity, an alternative
is to replace `logical_or` with a `impl_rhs` non-terminal:

```ebnf
?implication: logical_or | implication IMPL_OP impl_rhs
?impl_rhs: logical_or
          | "\\forall" CNAME ";" expr -> forall_expr
          | "\\exists" CNAME ";" expr -> exists_expr
```

(And similarly `or_rhs`, `and_rhs` for the other levels.)

### 2. Transformer update (Module2\_Parser.py, lines 243–245)

Add methods for the new rule aliases.  The three-argument form receives
`(left, op, var, body)` from the binary rule — but we discard `left` and `op`
at the transformer level?  No — Lark's `inline=True` will pass *all* matched
items.  Since `implication IMPL_OP \forall CNAME ; expr` has four "data" items
(the implication result, the IMPL\_OP token, the CNAME, the expr), the method
receives four arguments.

**However**, a cleaner approach is the `impl_rhs` variant above, which reuses
the existing `forall_expr` / `exists_expr` aliases.  With `impl_rhs`:

- No new transformer methods are needed.
- The `implication` method still receives `(left, op, right)` where `right`
  is now a `Forall`/`Exists` node returned by `forall_expr`/`exists_expr`.

For the inline approach (without `impl_rhs`), add:

```python
def impl_forall(self, _left_or_dummy, *args):
    # When called from implication: args = (op, var, body)
    # When called from logical_or/and: args = (op, var, body)
    # We need to reconstruct: BinOp(left, op, Forall(var, body))
    op = str(args[0])
    var = str(args[1])
    body = args[2]
    return BinOp(_left_or_dummy, op, Forall(var, body))

def impl_exists(self, _left_or_dummy, *args):
    op = str(args[0])
    var = str(args[1])
    body = args[2]
    return BinOp(_left_or_dummy, op, Exists(var, body))
```

### 3. No changes needed downstream

Modules 3–6 already handle `Forall` and `Exists` nodes wherever they appear
in the AST.  The grammar change only affects how the parser builds the tree;
the resulting nodes are identical.

### 4. Tests

Add parser-level tests to verify the new positions:

```python
parser = Module2_Parser()

# RHS of ==>
r = parser.parse_contract(
    r"ensures found == 1 ==> \forall i; i >= 0", line_number=1)
assert isinstance(r.expr, BinOp)           # BinOp(==>)
assert isinstance(r.expr.right, Forall)     # RHS is Forall

# RHS of 'and'
r = parser.parse_contract(
    r"requires n > 0 and \exists j; j < n", line_number=1)
assert isinstance(r.expr, BinOp)           # BinOp(and)
assert isinstance(r.expr.right, Exists)

# RHS of 'or'
r = parser.parse_contract(
    r"requires n == 0 or \forall i; i >= 0", line_number=1)
assert isinstance(r.expr, BinOp)
assert isinstance(r.expr.right, Forall)
```

Add integration tests with full pipeline + Why3 verification for a
contract like:

```python
#@ loop invariant found == 0 ==> \forall k; 0 <= k and k < i ==> arr[k] != target
```

### 5. Update skill-annotate.md

The quantifier section (line 93) should note that quantifiers can now appear
after `==>`, `and`, and `or` without parentheses.

### 6. Add `\exist` alias

While touching the grammar, also add `\exist` (singular) as a synonym:

```ebnf
| "\\exist"  CNAME ";" expr -> exists_expr
```

---

## Summary

| # | Task | Files | Effort |
|---|------|-------|--------|
| 1 | Grammar: allow quantifiers as RHS of `==>`, `and`, `or` | `Module2_Parser.py` | ~12 lines of grammar + ~10 lines of transformer |
| 2 | Grammar: add `\exist` alias | `Module2_Parser.py` | 1 line |
| 3 | Parser unit tests | `test_*.py` or new | ~20 lines |
| 4 | Integration tests with Why3 | `tests/manually_annotated/` | 1–2 new files |
| 5 | Update skill-annotate.md | `agents/skill-annotate.md` | ~3 lines |
| 6 | No changes needed | Modules 3, 4, 5, 6 | — |

### Risk: LALR conflicts

The main risk is that Lark's LALR parser may report shift/reduce or
reduce/reduce conflicts when quantifier keywords appear as alternatives
alongside the existing `logical_or` / `logical_and` continuations.

**Mitigation:** If direct alternatives cause conflicts, use the `impl_rhs` /
`or_rhs` / `and_rhs` intermediate non-terminals (shown above) which isolate
the choice behind a single reduction step, eliminating the conflict.

### Workaround (available today, no code changes)

Users can already nest quantifiers inside any operator by adding parentheses:

```python
#@ ensures found == 0 ==> (\forall k; 0 <= k and k < i ==> arr[k] != target)
```

This works because `( expr )` is an `atom` and `expr` includes quantifiers.
