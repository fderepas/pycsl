**Local reasoning** is a proof style where the solver checks a small, explicit
piece of evidence instead of reconstructing a fact from the whole structure.

An equivalent phrase often used in the repository is:

- **lookup-style reasoning**

---

## Why local reasoning matters in PyCSL

Local reasoning is usually the cheapest and most robust style for SMT-based
proofs.

It works especially well when the proof uses:

- ghost arrays
- ghost dictionaries
- ghost sets
- tuples
- small scalar summaries

These structures can act as [witness carriers](witness.md) that let the solver
prove a fact with one lookup or one-step relation.

---

## Concrete examples

### Map-style local reasoning

Instead of asking:

> “Is this node somewhere in the whole certified path?”

the proof asks:

> “What does `\map_get(certified_path, v)` say about this node?”

### Successor-style local reasoning

Instead of rebuilding an entire path sequence, the proof uses a local step such
as:

- `path_pos[parent[cur]] == path_pos[cur] + 1`

That is a typical local fact: one node, one successor, one cheap check.

### Whole-program invariants from local checks

A [HAPPY](happy.md) [meta-property](meta-property.md) turns a *global*,
whole-program guarantee ("no method writes outside the data region") into local
reasoning: it expands into one small `#@ check` per write site — each a cheap
local fact — and universal per-site coverage makes those local checks compose to
the global property, with no [global reasoning](global-reasoning.md) over the call
graph. It is how PyCSL gets a global property *out of* local reasoning.

---

## Related terms

- [witness](witness.md)
- [HAPPY](happy.md)
- [meta-property](meta-property.md)
- [solver budget](solver-budget.md)
- [global reasoning](global-reasoning.md)

> **In short:** local reasoning asks the prover to inspect the exact nearby fact
> it needs, not the whole mathematical universe around it.
