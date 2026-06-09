A **snapshot** is a frozen ghost copy of some runtime state taken at a specific
proof point. A **view** is a slightly broader term for a bounded or structured
representation of part of the state that the proof can inspect.

The two terms are closely related:

- a **snapshot** is usually a full frozen copy
- a **view** may be a segment, projection, or summarized perspective on the data

---

## Why snapshots and views matter in PyCSL

They let the proof talk about “before” and “after” without relying only on
global `\old(...)` expressions.

Common uses:

- prove a region of an array was not modified
- compare the current state to an earlier path or frontier state
- carry a bounded proof object instead of reconstructing the whole structure

This makes snapshots and views common building blocks for
[witnesses](witness.md).

---

## Concrete examples

```python
#@ ghost snap : array = \copy(arr)
```

This creates a ghost snapshot of the current array.

```python
#@ ghost orig_parent : array = \copy(parent)
```

This acts as a stable view of the original parent relation while the executable
array is being rewritten.

A range-restricted copy such as `\copy_range(arr, lo, hi)` would be an even more
explicit range view.

---

## Related terms

- [ghost state](ghost-state.md)
- [witness](witness.md)
- [memory model](memory-model.md)

> **In short:** a snapshot or view gives the proof a stable thing to compare
> against while the runtime state keeps changing.
