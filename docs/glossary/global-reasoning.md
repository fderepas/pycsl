**Global reasoning** is a proof style where the solver must reason about an
entire structure, often through broad quantified claims or sequence lemmas,
instead of using a small explicit local fact.

---

## Why global reasoning is expensive in PyCSL

Global reasoning is not wrong, but it is usually the first place where SMT
automation becomes fragile.

Typical triggers are:

- wide `forall` invariants
- sequence reconstruction
- list membership lemmas
- proofs that require the solver to infer a long chain of reachability facts

This is why global reasoning often consumes too much
[solver budget](solver-budget.md).

---

## Concrete examples

### Expensive list reasoning

When a proof asks the solver to reason about `\mem(x, l)` or many `\nth(...)`
relations across a whole ghost list, the solver may time out even if the idea is
mathematically sound.

### Expensive path reconstruction

In the union-find witness experiments, a full ghost-list path was expressive,
but it forced the solver into whole-path reasoning and made the VC set worse
than the more local ghost-array certificate.

---

## Avoiding global reasoning for whole-program invariants

A *whole-program* invariant — "no method except these two ever writes outside the
data region", "only `encrypt` reads `self.secret`" — looks like it must be proved
by global reasoning over every function. It does not have to be. A
[HAPPY](happy.md) [meta-property](meta-property.md) is precisely the technique for
getting a **global property out of local reasoning**: one high-level declaration
expands into a small per-site `#@ check` at *every* write/read site, each a cheap
local fact the solver discharges, and **universal per-site coverage** — not a
quantified claim over all functions — is what makes them compose to the
whole-program guarantee. HAPPY is the answer to "how do you enforce a
whole-program invariant without paying for global reasoning."

---

## Related terms

- [local reasoning](local-reasoning.md)
- [HAPPY](happy.md)
- [meta-property](meta-property.md)
- [solver budget](solver-budget.md)
- [witness](witness.md)

> **In short:** global reasoning makes the prover rediscover the whole picture;
> local reasoning gives it the exact piece it needs.
