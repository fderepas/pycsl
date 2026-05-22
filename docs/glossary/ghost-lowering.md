**Lowering** or **transpilation** is the translation process that turns
high-level PyCSL constructs into the lower-level WhyML structures consumed by
Why3 and the SMT solvers.

**Ghost lowering** is the ghost-specific slice of that broader translation step.

In repo vocabulary, **WhyML lowering** and **WhyML transpilation** usually refer
to the broader translation pipeline, while this page keeps the focus on the
ghost-heavy part.

In practice, the ghost-heavy part of lowering spans the IR emitter and the WhyML
transpiler:

- `Module5_IREmitter.py`
- `Module6_WhyMLTranspiler.py`

---

## Why ghost lowering matters in PyCSL

Proof quality depends not only on the source annotation, but also on how that
annotation is lowered.

Two source snippets can look simple in Python yet produce very different WhyML:

- a ghost list update may lower to `Cons`
- a ghost dictionary update may lower to `Map.set`
- a ghost array write may lower to direct array mutation

If ghost lowering is buggy, incomplete, or unexpectedly expensive, the proof can
fail even when the source annotation looks mathematically right.

---

## Concrete examples

### Example 1 — shorthand lowering

```python
#@ ghost log += i
```

This lowers to the ghost-list prepend operation in WhyML, not to numeric `+=`.

### Example 2 — in-place ghost array write

```python
#@ ghost snap[i] = 1
```

This lowers to direct mutation of the ghost array value in WhyML.

### Example 3 — why lowering details matter

Recent witness experiments exposed two real lowering-sensitive issues:

- array length emission had to use `Array.length` to avoid clashes with list
  theories
- ghost updates inside loop bodies could be sensitive to statement position

So ghost lowering is not just an implementation detail; it directly affects what
proofs are practical.

---

## Related terms

- [ghost code](ghost-code.md)
- [ghost state](ghost-state.md)
- [witness](witness.md)

> **In short:** ghost lowering is the step where PyCSL ghost code becomes the
> actual WhyML ghost machinery the prover sees.
