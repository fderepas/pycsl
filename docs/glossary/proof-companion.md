A **proof companion** is the generated `<file>.proofs/` directory that stores
Rocq proof scripts for the verification conditions SMT could not discharge
automatically.

---

## Why proof companions matter in PyCSL

Most VCs are discharged *Valid* by Alt-Ergo or Z3 within their per-goal time
budget. The proof companion is the fallback layer for the smaller set of hard VCs
the SMT solvers leave *Unknown* or *Timeout* and that need interactive Rocq
proof.

It also gives you a stable place to keep manual proof work while the source file
evolves.

---

## Concrete workflow

### Generate a proof companion

`pycsl --rocq DIR file.py` exports Rocq skeletons for the remaining VCs.

### Manual proof replay

`pycsl --rocq-proofs DIR file.py` replays the completed Rocq proofs against the
current obligations.

### Scratch proof directory

When source annotations change, it is often safer to generate a fresh temporary
proof directory first, compare the new VC set, and only then replace or merge
the retained proof companion.

---

## Why this term is broader than one script

The proof companion is not just the `.v` files. It is the whole retained
manual-proof layer attached to a source file: generated skeletons, completed
scripts, and replay against regenerated VCs.

---

## Related terms

- [verification condition](verification-condition.md)
- [solver budget](solver-budget.md)
- [reference test](reference-test.md)

> **In short:** the proof companion is the manual-proof sidecar for the VCs SMT
> leaves behind.
