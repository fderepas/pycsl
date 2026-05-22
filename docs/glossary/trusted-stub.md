A **trusted stub** is a contract-only function or imported definition whose
behavior is assumed rather than proved.

In PyCSL, trusted stubs usually appear in one of two places:

- library stubs under `data/lib_stubs/`
- sliced or imported functions that are modeled by contract in the current
  verification run

---

## Why trusted stubs matter in PyCSL

Trusted stubs let the prover reason about code it is not currently verifying,
such as standard-library calls, external modules, or non-selected functions.

They are useful, but they are also an explicit trust boundary: the proof relies
on the contract being accurate.

---

## Concrete examples

### Library stubs

A file in `data/lib_stubs/` can mark a function as `#@ \trusted` and supply
only its contract.

### Selective verification

When `pycsl --fun NAME file.py` verifies only part of a file, functions outside
the selected slice can be injected as trusted stubs so the chosen function still
has callable dependencies.

### Imported contracts

With multi-file verification, imported local functions may also be modeled as
trusted stubs when only their contracts are needed in the current run.

---

## Related terms

- [reference test](reference-test.md)
- [verification condition](verification-condition.md)

> **In short:** a trusted stub is a function the proof is allowed to assume,
> not re-prove.
