A function is **referentially transparent** (RT) when calling it with the same arguments always
yields the same result and has no observable effect — so a call can be replaced by its result
("substituted") without changing the program's meaning.

In PyCSL a function is RT iff it is:

- **pure** — `#@ assigns \nothing`, not `\trusted` / `\abstract`, not `\diverges`,
- **reads no mutable global** — it does not read a `#@ shared` / mutable module global (module
  *constants* are fine), and
- **calls only RT functions.**

RT is **inferred**, not annotated — PyCSL checks the predicate above rather than requiring a new
directive.

---

## Why referential transparency matters in PyCSL

PyCSL already emits a pure, non-method function as a Why3 `let function`, which is referentially
transparent **by construction**: it gives `forall x. f x = f x` (determinism) for free, with no
separately-emitted lemma. So RT is a property the backend hands you, not one you prove.

Its load-bearing use is **sound memoization**. A memoizing decorator (`@lru_cache`, `@cache`,
`@cached_property`) is observationally transparent — `lru_cache(f)(x) == f(x)` — *only* when `f` is
RT, so the decorated function keeps its own contract. Memoizing a function that is **not** RT
(reads mutable shared state, or has effects) is unsound and is **rejected** (UB-7.7), mirroring the
other [undefined-behaviour](trusted-stub.md) rejections.

---

## Concrete examples

### RT — safe to memoize

A `@lru_cache` pure recursive `fib(n)` reading only its argument is RT; a caller proves the same
postcondition with or without the decorator (corpus `0515`).

### Not RT — rejected

A `@lru_cache` function that reads a `#@ shared` counter is not RT — its result depends on hidden
state, so the cache would return stale values. PyCSL rejects it (corpus `0516`).

---

## Related terms

- [pure function](pure-function.md)
- [verification condition](verification-condition.md)
- [trusted stub](trusted-stub.md)

> **In short:** a referentially transparent function always returns the same result for the same
> inputs with no effects — the soundness condition for memoization, and free from Why3's
> `let function`.
