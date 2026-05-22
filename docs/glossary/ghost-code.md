In PyCSL, **ghost code** means verification-only code added to help the prover.
It includes `#@ ghost ...` declarations, ghost updates, and other logical
bookkeeping that exists for proof purposes and is erased from the final
executable meaning of the program.

Two older or more academic aliases are:

- **auxiliary code**
- **shadow code**

In this repository, **ghost code** is the preferred term.

---

## Why ghost code matters in PyCSL

Ghost code is how PyCSL lets a developer record proof-relevant facts without
changing runtime behavior.

Typical uses include:

- building a [witness](witness.md)
- recording a [snapshot / view](snapshot-view.md) of a structure
- tracking a set of processed nodes
- maintaining counters or summaries that make loop invariants provable

Because ghost code is verification-only, it lets the proof layer become richer
without polluting the executable algorithm.

---

## Concrete examples

```python
#@ ghost orig_parent : array = \copy(parent)
#@ ghost path_pos : array = \make(n, -1)
```

These lines introduce ghost code that helps prove properties of a path
compression loop, while leaving the runtime behavior unchanged.

```python
#@ ghost seen += i
```

This is ghost code that updates verification-only state so the invariant can
reason about which elements have already been processed.

---

## Related terms

- [ghost state](ghost-state.md)
- [ghost lowering](ghost-lowering.md)
- [witness](witness.md)

> **In short:** ghost code is the verification-only code you write so the prover
> can see the proof structure you intend.
