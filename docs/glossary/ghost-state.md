**Ghost state** is the verification-only state tracked by ghost variables in a
PyCSL-annotated program.

An older synonym is:

- **logical state**

In this repository, **ghost state** is the preferred term because it matches the
surface syntax (`#@ ghost ...`) and keeps the connection to ghost code obvious.

---

## Ghost code vs ghost state

- **Ghost code** is the verification-only code that declares or updates ghost
  variables.
- **Ghost state** is the data currently stored in those ghost variables.

So ghost code *manipulates* ghost state.

---

## Why ghost state matters in PyCSL

Ghost state gives the prover a place to store evidence that is awkward or too
expensive to rediscover from the runtime state alone.

Common uses:

- path certificates
- processed-element sets
- snapshots of the original array
- compact loop summaries

This is often the raw material from which a [witness](witness.md) is built.

---

## Concrete examples

```python
#@ ghost orig_parent : array = \copy(parent)
#@ ghost path_pos : array = \make(n, -1)
```

Here, `orig_parent` and `path_pos` are ghost state. They record facts the solver
needs but the executable algorithm does not.

```python
#@ ghost seen : ghost_set = \set_empty
```

This ghost state can represent the set of nodes or values already visited by a
loop.

---

## Related terms

- [ghost code](ghost-code.md)
- [witness](witness.md)
- [snapshot / view](snapshot-view.md)

> **In short:** ghost state is the verification-only data the prover is allowed
> to inspect, while the runtime program ignores it completely.
