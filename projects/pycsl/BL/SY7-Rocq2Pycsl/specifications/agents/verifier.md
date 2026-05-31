# SY7-Rocq2Pycsl — Verifier (Persona binding)

**Role:** Verifier
**Layer scope:** L2 → L5 for `src/rocq2pycsl/`

## Binding

bin/check-proof-crosscheck.sh (Rocq side)

## Responsibilities

- Define and run the test plan in [`../../tests/main.md`](../../tests/main.md).
- Report PASS / FAIL with concrete evidence.
- On FAIL, escalate to the Reconciliator per
  `cmmi-glue` Workflow 3.
