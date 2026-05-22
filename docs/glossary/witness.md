In PyCSL, a **witness** is the preferred term for a localized piece of
verification-only evidence carried in **ghost state** and maintained by
**ghost code** so the prover does not have to rediscover that fact from scratch.

Two common aliases are:

- **proof certificate**
- **local certificate**

All three refer to the same basic idea: a small packet of evidence that makes a
proof obligation cheaper.

---

## Preferred terminology

- **Primary term:** *witness*
- **Documented aliases:** *proof certificate*, *local certificate*
- **Witness carrier:** the concrete ghost data structure that stores the witness
  (for example a ghost array, ghost dictionary, ghost set, tuple, or a compact
  scalar summary)

A witness is not the same thing as all ghost code. A witness is a *use* of ghost
state: it is the specific part of the ghost state that carries the evidence the
solver needs right now.

---

## Why witnesses matter in PyCSL

SMT solvers operate under a limited **solver budget**. They are good at cheap,
explicit checks, but they struggle when asked to reconstruct long chains of
reasoning from large quantified structures.

A witness changes the shape of the task:

| Without a witness (global reasoning) | With a witness (local reasoning) |
| --- | --- |
| The solver must infer how a node, segment, or value relates to the entire structure. | The solver reads a small, explicit ghost fact or lookup. |
| Typical mechanism: broad quantifiers, list membership, sequence reconstruction. | Typical mechanism: one-step successor facts, map lookups, tuple fields, array reads. |
| Common result: timeout or out-of-memory. | Common result: fast proof search. |

This is why witness design in PyCSL usually aims for **local reasoning** before
falling back to more expensive **global reasoning**.

---

## Concrete examples

### Path / frontier witnesses

In the `0288.py` union-find work, a ghost array such as `path_pos` acts as a
witness by recording where each certified node sits on the original path toward
the root. That lets the prover use local facts like:

- `parent[cur] == orig_parent[cur]`
- `path_pos[parent[cur]] == path_pos[cur] + 1`

instead of reconstructing the entire path globally.

### Snapshot / view witnesses

A ghost snapshot such as `#@ ghost snap : array = \copy(arr)` can witness that a
region of the original state has not changed. This is a common way to prove that
an update touched only the intended cells.

### Sparse-map witnesses

A ghost dictionary or ghost set can witness that a specific node or key has
already been processed. The solver then performs a cheap lookup instead of
searching the whole structure.

---

## Related terms

- [ghost code](ghost-code.md)
- [ghost state](ghost-state.md)
- [ghost lowering](ghost-lowering.md)
- [snapshot / view](snapshot-view.md)
- [solver budget](solver-budget.md)
- [local reasoning](local-reasoning.md)
- [global reasoning](global-reasoning.md)

> **In short:** a witness is the exact local evidence you hand to the prover so
> it can stop guessing and start checking.
