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
- [method-call inlining](method-call-inlining.md)
- [bounded quantification](bounded-quantification.md)

### Inductive predicates and lemmas

- [inductive predicate](inductive-predicate.md)
- [introduction & inversion](introduction-and-inversion.md)
- [strict positivity](strict-positivity.md)
- [lemma function](lemma-function.md)
- [relational-consequence-via-lemma](relational-consequence-via-lemma.md)
- [inductive reflection](inductive-reflection.md)
- [`#@ uses` ordering citation](uses-ordering-citation.md)

### State and invariant vocabulary

- [class invariant](class-invariant.md)
- [mutex invariant](mutex-invariant.md)
- [HAPPY](happy.md)
- [meta-property](meta-property.md)
- [pure function](pure-function.md)
- [referential transparency](referential-transparency.md)
- [memory model](memory-model.md)
- [mixin](mixin.md)

### Solver and prover background

- [axiom registry](axiom-registry.md)
- [SMT solver](smt-solver.md)
- [SAT solver](sat-solver.md)
- [theorem prover](theorem-prover.md)
- [trusted computing base](trusted-computing-base.md)

### Project discipline and trust boundaries

- [load-bearing](load-bearing.md)
- [extreme rigor](extreme-rigor.md)
- [abstract op](abstract-op.md)
- [demand-driver](demand-driver.md)
- [emission-identical gate](emission-identical-gate.md)
- [standard libraries](standard-libraries.md)
- [backend-as-enforcer](backend-as-enforcer.md)

## Maintenance note

When a new recurring term appears in docs or skills, prefer one of these three
outcomes:

1. add a new page here
2. merge it into an existing glossary page
3. queue it in `more-vocabulary-*.md` until the next glossary wave

Conversely, when adding a new term to `test-suite/annotations.md` or a skill file,
check whether it has a canonical glossary page before defining it inline. If one
exists, add a short link rather than re-explaining the concept.
