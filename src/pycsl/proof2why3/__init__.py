"""proof2why3 — mechanical cross-check between cited Rocq/Lean
theorems and the Module 6 axiom registry.

v0 (this iteration): regex-based string-level normalization for the
gcd theorem family in 0342. Sufficient for proof-of-concept on the
canonical example; the production IR-based extraction + canonicalization
remain Phases 1-4 in sticky-01.md.

The v0 pipeline:

    Rocq `Check qn.` ─┐
                      ├─→ normalize → compare
    Lean `#check qn`  ─┘                  │
                                          ↓
    Module 6 `_AXIOM_REGISTRY[qn]` ─→ normalize ─→ 3-way diff

Three-way equality fingers the source of any disagreement.

See sticky-01.md for the full Phase 1-4 plan and the upgrade path
to a proper first-order IR.
"""
