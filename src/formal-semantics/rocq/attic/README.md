# Rocq attic — exploratory / superseded files

Files here are kept as historical reference. They are **not**
in the live build (`_CoqProject` does not include them) and
may carry `Admitted` stubs reflecting incomplete exploration.

## Inventory

- **`Phase6m_VcgSemBridge_Rocq9.v`** — exploratory Rocq 9 port
  of the Sub-β bridge proof. Carries 6+ `Admitted` stubs
  targeting the why3-semantics library import path on a
  hypothetical Rocq 9 toolchain. The PRODUCTION proof for
  Coq 8.20 lives in `../Phase6m_VcgSemBridge.v` (no
  `Admitted`, all theorems proved). Revive this file only if
  / when the project upgrades to Rocq 9.

## Why "attic" not "deletion"

The git history would preserve the content either way. We
keep `attic/` so a future maintainer reading the source tree
can find the exploratory work without having to dig through
history. The convention mirrors `src/self-annotate/attic/`.
