A **loop variant** is a non-negative integer expression that strictly decreases
on every iteration. It is the evidence that the loop terminates.

---

## Why loop variants matter in PyCSL

Correctness alone is not enough for a total-correctness proof. The prover also
needs a decreasing measure. A missing or weak variant leaves dedicated
termination VCs open even if the invariant is otherwise fine.

Common PyCSL patterns include:

- `n - i` for forward scans
- `right - left + 1` for shrinking windows
- `cur - r` for descending parent chains

Not every syntactic loop should receive a variant. For example, intentionally
unbounded control loops such as outer `while True:` thread-entry shells are
handled differently.

---

## Concrete examples

### Forward scan

If `i` increases from `0` to `n`, the usual variant is `n - i`.

### Shrinking interval

If both ends move inward, the variant is often the current interval width.

### What the prover checks

A loop variant usually triggers VCs for:

- non-negativity at loop entry
- preservation of non-negativity
- strict decrease across the body

---

## Related terms

- [loop invariant](loop-invariant.md)
- [verification condition](verification-condition.md)
- [solver budget](solver-budget.md)

> **In short:** a loop variant is the countdown that makes termination
> explicit.
