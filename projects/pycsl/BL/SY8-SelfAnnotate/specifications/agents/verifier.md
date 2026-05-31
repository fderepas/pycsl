# SY8-SelfAnnotate — Verifier (Persona binding)

**Role:** Verifier
**Layer scope:** L2 → L5 for `src/self-annotate/`

## Binding

bin/run-self-annotation-suite.sh + agent-meta-evaluator.py

## Responsibilities

- Define and run the test plan in [`../../tests/main.md`](../../tests/main.md).
- Report PASS / FAIL with concrete evidence.
- On FAIL, escalate to the Reconciliator per
  `cmmi-glue` Workflow 3.
