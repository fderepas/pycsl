A **loop invariant** is a property that must hold before the loop starts and
after every iteration. It is the main summary the prover carries through a loop.

---

## Why loop invariants matter in PyCSL

Without a loop invariant, the prover forgets too much at the loop back-edge.
Invariants tell it what remains true about counters, bounds, partial results,
and ghost witnesses.

Good PyCSL invariants are usually:

- true at loop entry
- easy to preserve
- strong enough to prove safety or the postcondition
- local enough to stay within the solver budget

---

## Concrete examples

### Counter and bounds invariants

Typical invariants in an array scan are:

- `0 <= i and i <= n`
- `total >= 0`

These feed both safety VCs and the final postcondition.

### Witness-preserving invariants

In path-compression-style proofs, a local witness fact such as
`parent[cur] == orig_parent[cur]` can be a better invariant than a wide global
reconstruction.

### Quantified invariants

A **quantified invariant** is simply a loop invariant that uses `\forall` or
`\exists`.

It can be powerful, but it is often more expensive than a local witness or
lookup-based invariant, so it should be used only when the local form is not
enough.

---

## Related terms

- [loop variant](loop-variant.md)
- [verification condition](verification-condition.md)
- [solver budget](solver-budget.md)
- [local reasoning](local-reasoning.md)
- [global reasoning](global-reasoning.md)

> **In short:** a loop invariant is the fact the prover must keep alive across
> every iteration.
