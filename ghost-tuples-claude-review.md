# Review of `ghost-tuples.md` — Claude

## Overall verdict

Simplest and cleanest of the six ghost-type plans; the Why3 model is correct and the
fixed-arity design is the right call, but two soundness holes must be closed before
landing.

---

## Key strengths

- **Correct identification of the existing bug**: the `Tuple → 0` fallback at Module6
  line 1377–1379 is documented and this plan provides the direct fix path.
- **Fixed-arity `tuple2`/`tuple3`/`tuple4`**: avoids fragile inference; Why3 product
  types are structural so arity must be known at emit time.
- **Let-destructure for access**: `\fst`, `\snd`, `\proj` correctly compile to
  `(let (x, _) = !p in x)` — this is the only access method in Why3 (no stdlib
  `fst`/`snd`). The plan correctly notes this.
- **No new Why3 imports**: product types are built-in to Why3, so no preamble additions
  are needed. This makes the feature self-contained.
- **Whole-tuple reassignment only**: consistent with Why3 tuple immutability; avoids
  introducing a separate record-mutation path.

---

## Critical issues

### Issue 1 — Unsound `\proj` fallback (must fix before landing)

Plan §5b last branch:
```python
# Fallback for dynamic index — not supported, emit 0
return "0"
```

This is unsound: `#@ assert \proj(t, k) == 0` would silently pass for any `t` and `k`.
A contract using this would prove vacuously. This must be a hard error, not a silent
fallback.

**Fix**: reject non-literal `\proj` index at Module4 semantic analysis:
```python
if not isinstance(node.index, IntLiteral):
    self._error(node, "\\proj index must be a non-negative integer literal")
```

### Issue 2 — Arity lookup is fragile

`_get_ghost_tuple_arity` resolves arity by looking up the variable name in
`self._ghost_tuple_vars`. If the same name is used in different scopes, or if the IR
expression is not a simple `Var` node (e.g., `\fst(\fst(p))` for nested tuples), the
lookup returns the default arity `2`, silently generating wrong destructure patterns.

**Fix**: carry the arity in the IR node directly. Since `ghost_type` is already in the
IR (`"ghost_type": "tuple2"`), extract arity at emit time:
```python
arity = int(stmt.get("ghost_type", "tuple2")[-1])
```
No name-to-arity dictionary needed.

### Issue 3 — `_iter_csl_children` missing for all 4 new nodes

Module4's scope walker (`_iter_csl_children`) must recurse into new expression nodes or
variable uses inside tuple expressions are invisible to scope analysis. Missing for:
- `MkTupleExpr.elts` (list of children)
- `FstExpr.tuple_expr`
- `SndExpr.tuple_expr`
- `ProjExpr.tuple_expr` and `ProjExpr.index`

Without this, `self._check_csl_expr()` will not visit variables inside `\mktuple(a, b)`
and Module4 will not flag uses of undeclared variables.

### Issue 4 — Self-annotated copies not mentioned

`src/self-annotate/rocq/Module6_WhyMLTranspiler.py` and the lean copy must be updated
when new ghost-type dispatch is added to Module6. These are not mentioned in the plan.

---

## `\snd` pattern correctness for arity > 2

The plan's pattern generation for `\snd` on `tuple3`:
```python
rest = ", ".join(["_"] * (arity - 2)) if arity > 2 else ""
pattern = f"_, _v1" + (f", {rest}" if rest else "")
```
For `tuple3`, `rest = "_"` and `pattern = "_, _v1, _"`.
This generates `(let (_, _v1, _) = !p in _v1)` — **correct**.
But this edge case should have an explicit test since it is easy to introduce an
off-by-one here.

---

## Suggestions

1. Replace the `\proj` silent fallback with a Module4 hard error (Issue 1).
2. Carry arity in IR; remove `_get_ghost_tuple_arity` (Issue 2).
3. Add `_iter_csl_children` for all 4 new expression nodes (Issue 3).
4. Add explicit test for `\snd` on `tuple3` and `\proj(t, 2)` on `tuple3`.
5. Document that `\proj` only accepts integer literals 0..N-1 in the skill files.
6. Update self-annotated copies (Issue 4).

---

## Suggested staging

**Phase 1 (ship this):** `\mktuple`, `\fst`, `\snd`, `\proj` (literal index only),
ghost tuple declaration and reassignment, shared `declared_type`/`GHOST_TYPE` infra,
Module4 arity validation.

**Defer:** `\old(!p)` interaction tests, arity > 4, any structural tuple equality beyond
`=`.

---

## Comparison with GPT review

**Agreement:**
- GPT correctly flags `_iter_csl_children` as missing.
- GPT correctly flags fragile arity inference.
- GPT correctly notes self-annotated copies are absent.
- GPT correctly says no Rocq/Lean theorem changes are needed.

**Additional issues (not in GPT review):**
- The silent `\proj → 0` fallback is a soundness hole, not just a missing feature — it
  must be a hard error, not a deferred improvement.
- The `\snd` pattern for arity > 2 is correct but untested; this should be an explicit
  regression test.

**Disagreement with GPT:**
- GPT says "scope reads under-defined" generically. The plan is actually well-scoped for
  a first version — the specific problem is the two soundness issues, not overall scope.
