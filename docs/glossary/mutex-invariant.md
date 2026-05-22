A **mutex invariant** is a property of shared state that PyCSL associates with
a lock in the concurrent memory model. It should hold whenever that mutex is
free.

In source, it is written as `#@ mutex_invariant <mutex>: <expr>` at module
level, typically next to `#@ shared` declarations and the `_ = 0  # anchor`
line used for module-level concurrency annotations.

---

## Why mutex invariants matter in PyCSL

PyCSL models a `#@ critical <mutex>` block by havocking the protected shared
variables, assuming the mutex invariant on entry, and asserting it on exit.

That makes the mutex invariant the main proof bridge between threads:

- it tells the prover what may be assumed after acquiring the lock
- it defines what each critical section must re-establish before releasing it
- it keeps shared-state reasoning local instead of forcing whole-program
  interleaving proofs

PyCSL also checks scope: the invariant may only mention variables protected by
that mutex.

---

## Concrete examples

### Non-negative shared counter

In `0250.py`:

```python
#@ shared counter protected_by lock_counter
#@ mutex_invariant lock_counter: counter >= 0
```

Inside the `#@ critical lock_counter` block, incrementing `counter` is valid
because the code re-establishes `counter >= 0` before the lock is released.

### Bounded shared temperature

In `0279.py`, the invariant is compound:

```python
#@ mutex_invariant lock_temp: temp >= 0 and temp <= 100
```

This shows that a mutex invariant can describe a range, not just a single lower
bound. Any critical section using `lock_temp` must leave `temp` back inside
that range.

---

## Related terms

- [memory model](memory-model.md)
- [class invariant](class-invariant.md)
- [verification condition](verification-condition.md)

> **In short:** a mutex invariant is the shared-state promise every critical
> section may assume on entry and must restore on exit.
