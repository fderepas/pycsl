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

## Transpiler limits in practice

A **transpiler limit** is a lowering or code-generation boundary that the source
program must model around. The issue is not the intended proof idea itself, but
that some Python-level shapes do not lower cleanly to the WhyML the prover sees.

Typical responses to a transpiler limit are:

- rewriting a compound guard into simpler control flow
- choosing constructs with a direct, predictable WhyML lowering
- avoiding shorthand that would emit unsupported or ambiguous code

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

### Example 3 — ghost dict update (option-type)

```python
#@ ghost d = \map_set(d, k, v)
```

This lowers to `Map.set !d k (Some v)` in WhyML, not the bare `Map.set !d k v`.
Ghost dicts use `map int (option int)` — present values are wrapped in `Some`,
absent keys are `None`. `\map_remove(d, k)` lowers to `Map.set !d k None`.

See `test-suite/annotations.md §11.9` for the full emission table.

### Example 4 — why lowering details matter

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
