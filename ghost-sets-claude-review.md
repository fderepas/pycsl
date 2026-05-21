# Review of `ghost-sets.md` — Claude

## Overall verdict

Best-designed of the six plans: `map int bool` model is excellent, the `pycsl_set_card_add`
lemma is correctly anticipated, and the `+=`/`-=` shorthands are a good UX decision.
The main blocker is a `\set_card` documentation inconsistency that must be resolved.

---

## Key strengths

- **`map int bool` → SMT-LIB `(Array Int Bool)`**: native boolean array theory in Z3
  and CVC5. Goals like `Map.get (Map.set s x true) x = true` discharge in < 0.01s by
  the array theory axiom. Stronger SMT automation than the `map int int` dict model for
  membership queries.
- **`\set_add`/`\set_remove`/`\set_mem` need no preamble functions**: they compile
  directly to `Map.set s x true`, `Map.set s x false`, `Map.get s x = true`. Only
  `use map.Map` needed for these three operations.
- **Bounded `\set_card(s, lo, hi)`**: correct solution to the infinite-domain
  cardinality problem. Explicit range avoids the "how many integers are in ℤ" issue.
- **`pycsl_set_card_add` lemma**: correctly included and correctly stated. This lemma is
  essential for proofs that add a fresh element and then assert `\set_card` increased by
  1. Without it, Z3 cannot discharge the cardinality increment.
- **`+=`/`-=` shorthands**: good ergonomics. Maps directly to `Map.set !s x true` and
  `Map.set !s x false`; no ambiguity.
- **Shared `use map.Map` + `use map.Const` with ghost dicts**: the plan correctly notes
  this and proposes a unified `needs_map` flag in the preamble scanner.
- **`val ghost function` for union/inter/diff**: using `val ghost function` with
  postconditions (rather than inline `function` definitions) means each call introduces
  an abstract value with a specified property. SMT can then reason about one membership
  query at a time without unrolling quantifiers over the full set. Good design.

---

## Critical issues

### Issue 1 — `\set_card` inconsistency between examples and design (must fix)

The motivating examples use `\set_card(seen)` (1 argument):
```python
#@ loop invariant \set_card(seen) <= i   # example 1
#@ loop invariant \set_card(seen) == i   # example 3
#@ ensures \set_card(seen, 0, n) == n    # example 2 (correct 3-arg form)
```
But Section D4 and the Why3 semantics table specify `\set_card(s, lo, hi)` (3
arguments). The grammar in Phase 1 also defines `\set_card` as 3-arg:
```lark
"\\set_card" "(" expr "," expr "," expr ")" -> set_card_expr
```

**Fix**: update all examples to use the 3-arg form `\set_card(seen, 0, n)`. Add a
documentation note: "The range [lo, hi) must cover all elements that could be in the
set; for arrays, use `\set_card(s, 0, n)` where `n` is the array length."

### Issue 2 — `set_union`/`set_inter`/`set_diff` quantifier instantiation risk

These three operations use `val ghost function` with postconditions containing
`forall x: int. ...`. While the `val ghost function` approach is correct in principle,
the `forall` in the postcondition means that when a user writes
`#@ ensures \set_mem(k, \set_union(s1, s2))`, the Why3 goal is:
```
forall x: int. Map.get result x = true <-> (Map.get s1 x = true \/ Map.get s2 x = true)
  ⊢  Map.get result k = true
```
Z3 must instantiate the universal with `x = k`. This usually works but can fail on
nested union expressions. The plan should include a test that Z3 handles a simple
`\set_union` membership check without manual instantiation.

### Issue 3 — `_ghost_set_vars` must be separate from Python runtime set handling

Module6 currently handles Python runtime `set()` (lowered to abstract `int` in hoare
model) and `SetLit` IR nodes. Ghost sets use `map int bool` and are completely different
from runtime sets. Without an explicit `self._ghost_set_vars: Set[str]`, a ghost set
variable could be routed through the existing Python-set lowering and produce wrong
WhyML.

**Fix**: add `self._ghost_set_vars: Set[str]` to `_reset_function_state`. In all points
where Module6 checks for set-typed variables, gate on `name not in self._ghost_set_vars`.

### Issue 4 — `\to_set` is in Phase 6 but should be clearly deferred

`\to_set(arr, lo, hi)` is a recursive ghost function with a `requires 0 <= lo` and
`requires hi <= length a` precondition. It is useful but orthogonal to the core set
operations. It should be explicitly marked as a separate optional feature, not just
"Phase 6."

---

## Minor notes

- `\set_eq(s1, s2)` compiles to `s1 = s2`. For `map int bool`, this is extensional
  equality (same as for `map int int` in ghost dicts). Should be documented: two ghost
  sets are equal iff they agree on all integer membership values.
- `pycsl_set_subset` is a `predicate`, not a `val ghost function`. This means it can be
  used in assertions but not as a computed value. This is correct — subset is a boolean
  predicate, not a set. The distinction should be noted.
- `_iter_csl_children` must be added for all 10 new expression nodes.
- Self-annotated copies not mentioned — same systematic omission as other plans.

---

## Suggestions

1. Fix all `\set_card` examples to use the 3-arg form (Issue 1).
2. Add a test for Z3 discharge of `\set_union` single-element membership (Issue 2).
3. Add `self._ghost_set_vars: Set[str]` to prevent runtime-set misclassification
   (Issue 3).
4. Mark `\to_set` as clearly deferred/optional (Issue 4).
5. Document `\set_eq` as extensional equality.
6. Add `_iter_csl_children` for all new nodes.
7. Update self-annotated copies.

---

## Suggested staging

**Phase 1 (ship this — membership/add/remove/empty):**
- `\set_empty`, `\set_add`, `\set_remove`, `\set_mem`
- `\set_subset`, `\set_eq`
- Ghost set declaration (ref-wrapped `map int bool`)
- `+=`/`-=` shorthands
- `self._ghost_set_vars` tracking
- Shared `use map.Map` + `use map.Const` flag with ghost dicts
- 3 reference tests (membership tracking, `+=` shorthand, subset)

**Phase 2 (after Phase 1 tests pass):**
- `\set_union`, `\set_inter`, `\set_diff` (quantified ops)
- Z3 discharge test for union membership

**Phase 3:**
- `\set_card(s, lo, hi)` + `pycsl_set_card_add` lemma
- Cardinality reference test

**Phase 4 (optional):**
- `\to_set(arr, lo, hi)` array-to-set conversion

**Requires ghost-dicts to be landed first** for shared `needs_map` flag infrastructure
(or land simultaneously).

---

## Comparison with GPT review

**Agreement:**
- GPT correctly flags the `\set_card` 1-arg vs 3-arg inconsistency.
- GPT correctly notes Module4/5 misclassification of `SetLit` vs ghost sets.
- GPT correctly recommends staged implementation (membership first, then algebra).
- GPT recommends a distinct IR/type tag — agreed, this is `self._ghost_set_vars`.

**Additional issues (not in GPT review):**
- The quantifier instantiation risk for `\set_union`/`\set_inter`/`\set_diff` and the
  need for an explicit Z3 test.
- `\set_eq` is extensional equality — this needs documentation so users understand
  when it proves vs. when it may be unprovable.
- `pycsl_set_subset` as a `predicate` vs. `val ghost function` distinction.

**Disagreement with GPT:**
- GPT says the scope is "optimistic." I disagree: Phase 1 (membership/add/remove) is
  well-scoped and can be landed independently. The plan's total scope is large but
  phasing correctly separates the easy parts from the hard ones.
