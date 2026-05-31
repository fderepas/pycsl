# SY5-PycslEmit — Verifier (Persona binding)

**Role:** Verifier
**Layer scope:** L2 → L5 for `src/pycsl_emit/`

## Binding

pycsl --no-proof emit-only mode

## Responsibilities

- Define and run the test plan in [`../../tests/main.md`](../../tests/main.md).
- Report PASS / FAIL with concrete evidence.
- On FAIL, escalate to the Reconciliator per
  `cmmi-glue` Workflow 3.
