A **class invariant** is a property of an object's fields that PyCSL expects
to hold whenever control enters or leaves a verified method.

In source, it is written as `#@ class invariant <expr>` immediately before the
`class` keyword, using the `""  # pycsl` anchor line so the annotation attaches
to the class definition.

---

## Why class invariants matter in PyCSL

A class invariant is the class-level summary that survives across method calls.

It matters because PyCSL checks it automatically at method boundaries, so:

- mutating methods need `requires` clauses strong enough to preserve it
- read-only methods with `#@ assigns \nothing` usually do not need extra
  invariant-guarding preconditions
- you do not need to restate the invariant as an `ensures` clause on every
  method

---

## Concrete examples

### Counter stays non-negative

In `test-suite/corpus/pycsl-reference/0006.py`, the class declares:

```python
""  # pycsl
#@ class invariant self._value >= 0
class Counter:
```

The `increment` method then requires `amount >= 0`, which is exactly the kind
of precondition that keeps the invariant true after mutation.

### Interval fields stay ordered

In `0191.py`, the invariant is `self._lo <= self._hi`.

That forces the setters to guard both sides of the relation:

- `set_lo` requires `lo <= self._hi`
- `set_hi` requires `hi >= self._lo`

The read-only `width` method uses `#@ assigns \nothing`, so it can rely on the
invariant without changing object state.

---

## Related terms

- [loop invariant](loop-invariant.md)
- [pure function](pure-function.md)
- [verification condition](verification-condition.md)

> **In short:** a class invariant is the object-state fact PyCSL keeps true
> across every method boundary.
