# SY3-Pycsl — Verifier (Persona binding)

**Role:** Verifier
**Layer scope:** L2 → L5 for `src/pycsl/`

## Binding

pycsl --proof + bin/run-reference-tests.sh + bin/doc-coherency.py

## Responsibilities

- Define and run the test plan in [`../../tests/main.md`](../../tests/main.md).
- Report PASS / FAIL with concrete evidence.
- On FAIL, escalate to the Reconciliator per
  `cmmi-glue` Workflow 3.
