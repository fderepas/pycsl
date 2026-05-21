# Review of `ghost-lists.md` — Claude

## Overall verdict

Core design is correct (immutable `list int`, ref-wrapped), but Phase 1 scope is too
broad and two runtime-classification clashes in Module6 will cause silent miscompilation
unless addressed explicitly.

---

## Key strengths

- **Immutable `list int` with ref-wrap is the right model**: Why3's `list` is an
  inductive recursive type, not mutable in place. The only way to "update" a ghost list
  is to reassign the ref to a new `list int` value. Ref-wrap is necessary and correct.
- **`\nil`/`\cons`/`\hd`/`\tl` map directly to Why3**:
  - `\nil` → `Nil` (constructor)
  - `\cons(x, l)` → `Cons x !l`
  - `\hd(l)` → `List.hd !l`
  - `\tl(l)` → `List.tl !l`
  These are zero-preamble operations; `use list.List` suffices.
- **`\list_length(l)` → `List.length !l`**: correct; Why3's `List.length` is a
  recursive function returning a non-negative `int`.
- **`\mem(x, l)` → `List.mem x !l`**: correct for integer membership; Why3's `List.mem`
  uses structural equality which works for `int`.
- **Acknowledges `\to_list` complexity**: the plan defers array-to-list conversion to
  Phase 5, which is appropriate.
- **`\append` and `\concat`**: useful for trace-accumulation specs; compile to
  `List.append` which is in the Why3 stdlib.

---

## Critical issues

### Issue 1 — Module6 list/array classification clash

Module6 classifies a Python variable as an "array" if its type annotation is `list`
(Python's `list` type hint). A ghost variable declared:
```python
#@ ghost l : list = \nil
```
has Python type annotation inferred as `list`, and the transpiler's array-classification
logic may add it to `self._array_locals`.

This is worse than just a naming collision: if `l` ends up in `_array_locals`, Module6
will:
1. Attempt to emit `(length !l)` as the array size — type error (`!l : list int`, not
   `array int`).
2. Include `l` in the `known_collection_sizes` tracking.
3. Potentially emit `l.(i)` instead of `List.nth !l i` for access.

**Fix**: use `declared_type == "ghost_list"` (not `"list"`) as the canonical tag
throughout Module4/5/6. When the IR carries `"ghost_type": "ghost_list"`, Module6
bypasses all `_array_locals` paths. Do NOT use `"list"` as the ghost type tag — it
collides with the runtime list annotation.

### Issue 2 — `List.nth` raises exception on out-of-bounds

Why3's `List.nth l i` is partial: it raises `Not_found` if `i >= List.length l`. A
`#@ assert \nth(l, i) == x` with no precondition will generate a Why3 goal that
requires proving `i < List.length l` as a side condition. If the user does not provide
the precondition, Why3 will report an unproved obligation that may be confusing.

**Fix**: document that `\nth` requires `requires 0 <= i and i < \list_length(l)` at the
call site. Generate a Module4 warning if `\nth` is used without a visible bound
precondition on the index.

### Issue 3 — Phase 1 scope too broad

The plan lists these operations in Phase 1 and/or Phase 5 without clearly separating
what is required for a minimal usable release:
- `\nil`, `\cons`, `\hd`, `\tl`, `\list_length`, `\nth`, `\mem`, `\append` — usable
- `\concat`, `\reverse` — convenient but not essential
- `\to_list`, `\sorted_list`, `\is_permutation_list` — complex, should be a separate
  plan

The `\to_list` conversion requires a recursive ghost function that iterates over an
array and builds a list; it depends on both ghost lists AND the active memory model's
array representation. This is non-trivial and orthogonal to the core list operations.

**Fix**: scope Phase 1 to 8 operations: `\nil`, `\cons`, `\hd`, `\tl`, `\list_length`,
`\nth`, `\mem`, `\append`. Move `\reverse` to Phase 2. Defer `\concat`, `\to_list`,
`\sorted_list`, `\is_permutation_list` to a separate plan.

### Issue 4 — `_iter_csl_children` missing for new list expression nodes

Module4's scope walker must recurse into all new list AST nodes:
- `ConsExpr.head` and `ConsExpr.tail`
- `HdExpr.list_expr`
- `TlExpr.list_expr`
- `ListLengthExpr.list_expr`
- `NthExpr.list_expr` and `NthExpr.index`
- `MemExpr.elem` and `MemExpr.list_expr`
- `AppendExpr.left` and `AppendExpr.right`

Without this, variable uses inside these expressions are invisible to Module4's scope
analysis.

### Issue 5 — Self-annotated copies not mentioned

`src/self-annotate/rocq/Module6_WhyMLTranspiler.py` and the lean copy must be updated
when ghost list dispatch is added to Module6. Absent from the plan.

---

## Minor notes

- `\mem(x, l)` for lists performs a linear scan; for membership in sets, ghost sets
  are more appropriate. The plan should add a usage note: "Use `\mem` for list specs
  (ordered sequences, multisets); use `\set_mem` for unordered membership (ghost-sets.md)."
- `\list_length(l)` returns a non-negative integer. If `l` is `\nil`, it returns 0.
  This is safe and does not need a precondition.
- Ghost list variables are in `local_refs` after declaration (ref-wrapped), so the
  existing Var handler already emits `!l` for dereference. No change needed there.
- `use list.List` must be added to the preamble when any ghost list is used. Track with
  a `needs_ghost_list` flag.

---

## Suggestions

1. Use `"ghost_list"` as the `declared_type`/`ghost_type` tag throughout (not `"list"`)
   to avoid the array-classification clash (Issue 1).
2. Document `\nth` precondition requirement; add Module4 warning for unguarded `\nth`
   use (Issue 2).
3. Narrow Phase 1 scope to 8 core operations; move `\reverse` to Phase 2; defer
   `\to_list`/`\sorted_list`/`\is_permutation_list` to a separate plan (Issue 3).
4. Add `_iter_csl_children` for all new AST nodes (Issue 4).
5. Update self-annotated copies (Issue 5).
6. Add usage note distinguishing list `\mem` from set `\set_mem`.
7. Add `needs_ghost_list` preamble flag for `use list.List`.

---

## Suggested staging

**Phase 1 (ship this — core 8 operations):**
- `\nil`, `\cons`, `\hd`, `\tl`, `\list_length`, `\nth`, `\mem`, `\append`
- Ghost list declaration (ref-wrapped `list int`)
- `declared_type = "ghost_list"` throughout (NOT `"list"`)
- `self._ghost_list_vars: Set[str]` tracking
- `use list.List` preamble flag
- `_iter_csl_children` for all 8 operation nodes
- Module4 `\nth` index bound warning
- 3 reference tests (nil/cons, length, membership)

**Phase 2:**
- `\reverse`, `\concat`
- Test: `\mem` after `\cons`

**Defer (separate plan):**
- `\to_list(arr, lo, hi)` — requires array-to-list ghost function; depends on memory
  model; complex
- `\sorted_list` — requires ordering predicate
- `\is_permutation_list` — requires multiset equality lemmas; will timeout

---

## Comparison with GPT review

**Agreement:**
- GPT correctly flags `_iter_csl_children` as missing.
- GPT correctly identifies the list/array classification clash in Module6.
- GPT recommends using `declared_type = "ghost_list"` end-to-end — strongly agreed.
- GPT recommends deferring `\to_list` and permutation helpers — strongly agreed.
- GPT notes self-annotated copies are absent — agreed.

**Additional issues (not in GPT review):**
- `List.nth` out-of-bounds exception semantics need a documented precondition and
  a Module4 warning. GPT does not mention this.
- `\mem` vs `\set_mem` usage note is important for users choosing between list/set
  representation for their spec.

**Disagreement with GPT:**
- GPT says "major revision needed." The core design (immutable list, ref-wrapped,
  `\nil`/`\cons`) is correct and does not need revision — only the scope and two
  specific issues (classification clash, `\nth` bound) need fixes. "Major revision"
  overstates it.
