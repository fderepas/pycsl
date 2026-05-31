# SY8-SelfAnnotate — Test Plan

**Document ID:** TEST-PYCSL-SY8-001
**Layer:** L2 (System integration tests)

---

## Source code under test

`src/self-annotate/`

## Verifier binding

bin/run-self-annotation-suite.sh + agent-meta-evaluator.py

## Acceptance criteria

This System is "L2-complete" when its bound verifier exits 0 against
the full source surface. Per-component (L3) and per-module (L4) test
plans appear under `CO<M>-<Name>/tests/` and `MO<P>-<Name>/tests/`
respectively (auto-generated for L4 by `bin/cmmi-mod-index.py`).

---

## Reconciliator binding

coordinator.py exit 72/73 + agent-meta-monitor.py + agent-meta-reviewer.py

The Reconciliator is invoked when the Verifier reports a failure
that exceeds the per-System retry budget.
