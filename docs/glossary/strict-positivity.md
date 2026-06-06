**Strict positivity** is the soundness condition on an [inductive
predicate](inductive-predicate.md)'s rules: the predicate being defined may occur
in a rule's premises only *positively* — never under a negation, and never in the
antecedent of a nested implication. It guarantees the least fixpoint actually
exists.

---

## Why it matters

An inductive predicate is the *least* fixpoint of its rules. If a rule used the
predicate negatively — e.g. `(not p(x)) ==> p(x)` — there might be no consistent
least fixpoint, and an unsound definition could let you derive `False`. Strict
positivity is the standard restriction (from inductive type theory) that rules
this out.

A rejected shape (the negative-driver pattern, since PyCSL's `not` does not parse
inside a rule clause the way the spec's Horn syntax assumes) is a nested
implication that buries the predicate in an antecedent:

```python
#@ inductive bad(n: int):
#@     bad_step: \forall m: int; (bad(m) ==> bad(m)) ==> bad(m + 1)
```

## Who enforces it

**Why3**, at verification time: a non-strictly-positive rule is rejected with
`non strictly positive occurrence …`. PyCSL emits the `inductive` declaration and
relies on the backend — see [backend-as-enforcer](backend-as-enforcer.md). The
check is **group-wide** for [mutually-inductive](inductive-predicate.md) `with`
groups (a non-positive occurrence in a `with`-member is rejected too).

A Module-4 pre-check (an earlier, cleaner diagnostic) is a documented refinement,
not a soundness gap — Why3 already closes the hole.

Drivers `0563` (single predicate), `0575` (mutual group).
