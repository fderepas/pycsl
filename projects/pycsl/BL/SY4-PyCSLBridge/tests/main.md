# SY4-PyCSLBridge — Test Plan

**Document ID:** TEST-PYCSL-SY4-001
**Layer:** L2 (System integration tests)

---

## Source code under test

`src/pycsl_bridge/`

## Verifier binding

smoke tests in tests/

## Acceptance criteria

This System is "L2-complete" when its bound verifier exits 0 against
the full source surface. Per-component (L3) and per-module (L4) test
plans appear under `CO<M>-<Name>/tests/` and `MO<P>-<Name>/tests/`
respectively (auto-generated for L4 by `bin/cmmi-mod-index.py`).

---

## Reconciliator binding

developer

The Reconciliator is invoked when the Verifier reports a failure
that exceeds the per-System retry budget.
