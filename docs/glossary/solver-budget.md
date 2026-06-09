The **solver budget** is the finite amount of time (a per-goal limit of roughly
30 seconds), memory, and quantifier-instantiation search that a tool like
Alt-Ergo or Z3 can spend on a single
[verification condition](verification-condition.md) before it returns
`Unknown`, times out, or runs out of memory.

An **SMT-hard goal** is simply a VC that is mathematically reasonable but still
too expensive for the available solver budget.

---

## Why solver budget matters in PyCSL

PyCSL annotations are not judged only by mathematical correctness. They are also
judged by whether the generated verification conditions are cheap enough for the
SMT solvers to discharge.

This is why proof engineering in PyCSL often prefers:

- explicit ghost lookups
- compact witness carriers
- one-step successor facts

over:

- broad quantified invariants
- global list membership reasoning
- whole-structure reconstruction

---

## Solver heuristics in practice

A **solver heuristic** is the practical annotation or proof-pattern choice you
make to stay within the solver budget. The goal does not change; the encoding
does.

Typical heuristics in PyCSL include:

- replacing wide quantified claims with local witness facts
- using direct ghost lookups instead of reconstructed whole-structure facts
- splitting one expensive invariant into a few cheaper ones

---

## Concrete examples

Two recurring budget failures are:

- `\mem(x, l)`-style ghost-list reasoning in loop invariants
- full path-list witnesses that forced the solver into wide quantified
  instantiation

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
