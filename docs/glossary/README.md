# PyCSL glossary

This directory is the human-facing glossary for recurring PyCSL terms used
across the README, skills, and reference documents.

Use these pages when you want the **repo-facing meaning** of a term, not the
full normative rule set from:

- `docs/pycsl-concrete-syntax-reference.md`
- `docs/pycsl-static-semantics-reference.md`
- `docs/pycsl-translational-reference.md`

The glossary prefers one primary term per concept and records aliases inside the
relevant page when needed.

## Index

### Core verification workflow

- [verification condition](verification-condition.md)
- [loop invariant](loop-invariant.md)
- [loop variant](loop-variant.md)
- [proof companion](proof-companion.md)
- [reference test](reference-test.md)
- [trusted stub](trusted-stub.md)

### Ghost code and proof structure

- [witness](witness.md)
- [ghost code](ghost-code.md)
- [ghost state](ghost-state.md)
- [ghost lowering](ghost-lowering.md)
- [snapshot / view](snapshot-view.md)
- [local reasoning](local-reasoning.md)
- [global reasoning](global-reasoning.md)
- [solver budget](solver-budget.md)

### State and invariant vocabulary

- [class invariant](class-invariant.md)
- [mutex invariant](mutex-invariant.md)
- [pure function](pure-function.md)
- [memory model](memory-model.md)

### Solver and prover background

- [SMT solver](smt-solver.md)
- [SAT solver](sat-solver.md)
- [theorem prover](theorem-prover.md)

## Maintenance note

When a new recurring term appears in docs or skills, prefer one of these three
outcomes:

1. add a new page here
2. merge it into an existing glossary page
3. queue it in `more-vocabulary-*.md` until the next glossary wave
