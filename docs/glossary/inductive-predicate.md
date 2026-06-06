An **inductive predicate** is a logic-level relation defined as a *least fixpoint*
by a set of Horn-clause introduction rules — used for properties that are not a
terminating boolean function (well-formedness, reachability, typing judgements).

In source, it is a module-level block:

```python
#@ inductive even(n: int):
#@     even_zero: even(0)
#@     even_step: \forall m: int; even(m) ==> even(m + 2)
```

The rules are bare `name: clause` lines indented 4 spaces under the header (there
is **no** `rule` keyword — it was retired). It lowers to a Why3
`inductive even int = | Even_zero : even 0 | Even_step : … ` (a single predicate
takes **no** closing `end`).

---

## Logic-only

A predicate is usable in any contract — `#@ requires`, `#@ ensures`, loop
invariants, `#@ lemma` — but is **never executable**: it has no runtime value, so
it cannot appear in a function body's computation. To compute with it you need
[inductive reflection](inductive-reflection.md) (a decision function + agreement
lemma).

## What you get from it

- **Forward** — [introduction](introduction-and-inversion.md): prove a concrete
  instance (`even(4)`) by applying rules.
- **Backward** — [inversion](introduction-and-inversion.md): a value can only have
  been built by the rules (`not even(3)`).
- **Over the whole relation** —
  [relational-consequence-via-lemma](relational-consequence-via-lemma.md): a
  universally-quantified fact (`\forall n; even(n) ==> n >= 0`) needs the
  predicate's induction principle, supplied through a [`#@ lemma`](lemma-function.md).

## Variants

- **Mutually-inductive groups** — a `#@ with q(sig):` continuation block joins `q`
  into the same least-fixpoint group (`even`/`odd`), emitting one
  `inductive p … with q … `.
- **Relational form** — a non-structural, multi-arg predicate
  (`reach(x+1, z) ==> reach(x, z)`), which a terminating function cannot express.

## Soundness

Rules must satisfy [strict positivity](strict-positivity.md) (the predicate occurs
only positively in premises), which guarantees the least fixpoint exists. Why3
enforces this; PyCSL emits the declaration and relies on the backend
([backend-as-enforcer](backend-as-enforcer.md)).

Drivers `0562` (even), `0572` (reachability), `0574`/`0575` (mutual). See
`test-suite/annotations.md` §2.8.
