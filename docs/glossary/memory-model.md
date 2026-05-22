In PyCSL, a **memory model** is the semantic framework the verifier uses to
interpret reads, writes, aliasing, and heap-like behavior.

The same source annotation can mean slightly different things depending on which
memory model is selected.

---

## Why memory models matter in PyCSL

Different verification tasks need different trade-offs:

- simpler models are easier for SMT to prove automatically
- richer models can express aliasing and heap structure more faithfully

So “memory model” is not just an implementation flag. It changes what kinds of
proof obligations the tool generates and what ghost encodings are convenient.

---

## The four PyCSL memory models

| Model | Human-facing summary |
| --- | --- |
| `hoare` | The simplest model. Arrays behave like value-semantic structures and are the easiest setting for ghost arrays and snapshots. |
| `typed` | An explicit heap/reference model for pointer-like reasoning, validity, and separation-style constraints. |
| `store` | Very close to `typed`, but with a different internal heap representation name. |
| `concurrent` | Extends the basic reasoning model with shared state, mutex invariants, and critical sections. |

---

## Concrete examples

- A ghost array snapshot such as `\copy(arr)` is most natural in the **Hoare
  model**.
- `\valid(arr, n)` and `\separated(a, na, b, nb)` belong to the richer
  **typed/store** style of reasoning.
- Shared-variable verification with mutex invariants belongs to the
  **concurrent** model.

For the deeper technical design discussion, see the main document:

- [`docs/memory_model.md`](../memory_model.md)

---

## Related terms

- [ghost code](ghost-code.md)
- [snapshot / view](snapshot-view.md)

> **In short:** the memory model tells PyCSL what kind of state it is reasoning
> about, and therefore what proof style is available.
