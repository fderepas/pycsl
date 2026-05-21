# Review of `ghost-array.md` — Claude

## Overall verdict

Sound fundamental design (no ref-wrap is correct; `GhostArraySetDecl` as a separate
node is right), but the Module6 interaction surface is significantly larger than
documented and `\is_permutation` will cause solver timeouts in practice.

---

## Key strengths

- **Correct no-ref-wrap decision**: Why3's `array int` is already mutable in-place via
  `a.(i) <- v`. Adding a `ref` layer would require double-dereference (`(!a).(i)`) and
  complicate all array-access expressions. The plan's rationale is sound.
- **`GhostArraySetDecl` as a separate AST node**: element-level assignment
  (`ghost a[i] = expr`) is semantically different from whole-variable assignment
  (`ghost a = \copy(arr)`). A separate node avoids forcing element-set through the
  `GhostAssignDecl` path and enables precise Module4 validation.
- **`\copy(arr)` → `Array.copy a`**: this is the correct Why3 stdlib call for a
  snapshot that is independent of further mutations to `arr`.
- **`\make(n, v)` → `Array.make n v`**: standard Why3 constructor, no preamble function
  needed.

---

## Critical issues

### Issue 1 — `_array_locals` collision in Module6

Module6 tracks runtime array parameters in `self._array_locals`. The existing logic
classifies a variable as an array if its type annotation is `list` (Python) or if it
appears in array-typed IR. A ghost variable declared `ghost snap : array = \copy(arr)`
could fall into this classification and be added to `_array_locals`, causing it to
receive `(length snap)` size tracking, ghost parameter emission, or other array-specific
treatment meant only for runtime arrays.

**Fix**: add `self._ghost_array_vars: Set[str]` to `_reset_function_state`. Populate it
when a ghost array declaration is processed. At all points where `_array_locals` is
consulted, gate on `name not in self._ghost_array_vars`.

### Issue 2 — Memory model ambiguity for `\copy(arr)`

In the hoare model, `arr` is a `array int` value — `Array.copy arr` works directly.

In the typed/store model, `arr` is an abstract pointer and array contents are in
`!int_mem`. `Array.copy arr` would copy the pointer, not the heap contents. Ghost arrays
should always use the **hoare-model `Array.array int` type** regardless of the active
memory model, because they are specification-only (not heap-allocated).

The plan does not state this. Without this specification:
- In typed/store model, `\copy(arr)` would need to be `Array.make n 0` initialized with
  a `for`-loop reading from `!int_mem` — completely different code.
- Users would get silent type errors when switching memory models.

**Fix**: explicitly state in the design that ghost arrays always use `Array.array int`
(hoare-model type), and that `\copy(arr)` in typed/store model copies the array's
logical content by reading `!int_mem`.

### Issue 3 — `\is_permutation` solver timeout

The plan implements `\is_permutation(a, b, n)` via a recursive `pycsl_count` function:
```why3
let rec ghost function pycsl_count (a: array int) (x lo hi: int) : int
  variant { hi - lo }
= ...
```
This requires Z3 to reason about `pycsl_count(a, x, 0, n) = pycsl_count(b, x, 0, n)`
for all `x` in the range. In practice, SMT solvers cannot handle this without
significant manual lemmas about `pycsl_count` monotonicity and commutativity. Expect
timeouts for `n > 15` even with `--steps 10000000`.

**Fix**: defer `\is_permutation` to a separate plan. As an immediate alternative, point
users to ghost sets (`\to_set(arr, 0, n)`) for element-presence checking (not
multiset). Add a note in the plan: "`\is_permutation` deferred — requires an external
permutation axiom or significant manual lemmas."

### Issue 4 — `_iter_csl_children` missing

Module4's scope walker must recurse into:
- `GhostArraySetDecl.index` and `GhostArraySetDecl.value`
- `CopyExpr.arr`
- `MakeExpr.size` and `MakeExpr.default`
- `GhostArrayGetExpr.arr` and `GhostArrayGetExpr.index`
- `IsPermutationExpr` (if kept)

Without this, variable uses inside these expressions are invisible to Module4's scope
analysis.

### Issue 5 — Self-annotated copies not mentioned

`src/self-annotate/rocq/Module6_WhyMLTranspiler.py` and the lean copy must be updated
when ghost array dispatch is added to `_handle_ghost_assign_stmt`.

---

## Suggestions

1. Add `self._ghost_array_vars: Set[str]` and exclude these from all `_array_locals`
   paths (Issue 1).
2. Specify in the design that ghost arrays always use `Array.array int` regardless of
   memory model, and document how `\copy` works in each model (Issue 2).
3. Defer `\is_permutation`; point users to ghost sets for element-presence. Add explicit
   deferral note to the plan (Issue 3).
4. Add `_iter_csl_children` entries for all new AST nodes (Issue 4).
5. Update self-annotated copies (Issue 5).
6. Add a "coexistence with typed/store model" subsection explicitly.

---

## Suggested staging

**Phase 1 (ship this):**
- `\make(n, v)` and `\copy(arr)` — ghost array creation
- `ghost a[i] = expr` — element assignment via `GhostArraySetDecl`
- `\glength(a)` — array length in contracts
- Hoare-model only; document typed/store as deferred
- `self._ghost_array_vars` tracking
- `_iter_csl_children` for all new nodes
- 2 reference tests (snapshot + element set)

**Phase 2:**
- Typed/store model support for `\copy`
- `\gget(a, i)` in contracts (if not already covered)
- Investigate `\is_permutation` feasibility with an explicit lemma approach

**Defer:**
- `\is_permutation` (solver-heavy; needs external lemma or separate plan)
- Multi-dimensional ghost arrays

---

## Comparison with GPT review

**Agreement:**
- GPT correctly flags that many Module6 array-sensitive paths are not covered.
- GPT correctly recommends gating the first version to hoare model.
- GPT correctly recommends deferring `\is_permutation`.
- GPT correctly flags memory-model differences as under-specified.

**Additional issues (not in GPT review):**
- The specific `_array_locals` collision mechanism (not just "many paths not covered" —
  the exact variable `self._array_locals` would misclassify ghost arrays).
- The memory-model issue is more concrete: `Array.copy` copies the hoare-model value,
  but in typed/store model the array content is in the heap. Ghost arrays must be
  spec-only `Array.array int` in all models.

**Disagreement with GPT:**
- GPT says the doc "overstates current support." More precisely: the plan's current-state
  table is largely accurate for the columns it covers, but is missing the `_array_locals`
  column which is the critical collision risk.
