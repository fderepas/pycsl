The **solver budget** is the finite amount of time, memory, and proof search a
tool like Alt-Ergo or Z3 can spend on a single
[verification condition](verification-condition.md) before it returns
`Unknown`, times out, or runs out of memory.

An **SMT-hard goal** is simply a VC that is mathematically reasonable but still
too expensive for the available solver budget.

---

## Why solver budget matters in PyCSL

PyCSL annotations are not judged only by mathematical correctness. They are also
judged by whether the generated verification conditions are cheap enough for the
automatic provers to discharge.

This is why proof engineering in PyCSL often prefers:

- explicit ghost lookups
- compact witness carriers
- one-step successor facts

over:

- broad quantified invariants
- global list membership reasoning
- whole-structure reconstruction

---

## Concrete examples

Two recurring budget failures in recent work were:

- `\mem(x, l)`-style ghost-list reasoning in loop invariants
- full path-list witnesses that forced the solver into wide quantified proofs

In both cases the issue was not that the idea was false. The issue was that it
spent too much solver budget.

---

## Related terms

- [verification condition](verification-condition.md)
- [local reasoning](local-reasoning.md)
- [global reasoning](global-reasoning.md)
- [witness](witness.md)

> **In short:** solver budget is the practical limit that separates a beautiful
> proof idea from a provable one.
