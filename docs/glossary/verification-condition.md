A **verification condition (VC)** is a single proof goal emitted by PyCSL and
Why3 from contracts, loop annotations, and program operations. One function
typically generates many VCs.

**Proof obligation** is the closest near-synonym. In PyCSL glossary usage,
**VC** is the shorter preferred term when talking about one generated goal.

---

## Why VCs matter in PyCSL

PyCSL does not prove a function in one monolithic step. It proves many smaller
goals, such as:

- array-bounds safety
- postcondition discharge
- loop invariant initialization
- loop invariant preservation
- loop variant decrease

This is why a source edit can improve proof behavior without changing runtime
behavior: it changes the VC set.

---

## Concrete examples

### One loop, many VCs

A loop with invariants and a variant usually creates separate VCs for:

- invariant holds at loop entry
- invariant is preserved
- variant is non-negative
- variant strictly decreases
- each loop-body safety check

### SMT first, Rocq later

If Alt-Ergo or Z3 discharges a VC, no manual action is needed.

If a VC remains open, `--rocq` can export it into a
[proof companion](proof-companion.md) for Rocq.

---

## Related terms

- [loop invariant](loop-invariant.md)
- [loop variant](loop-variant.md)
- [solver budget](solver-budget.md)
- [proof companion](proof-companion.md)

> **In short:** a VC is one generated proof goal, not the whole proof.
