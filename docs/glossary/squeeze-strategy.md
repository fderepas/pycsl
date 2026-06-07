**The Squeeze Strategy** is the meta-principle of the `*CSL` methodology: stack
independent constraint layers — *squeezes* — each with a mechanical gate, so that
**only a correct implementation survives all of them**. A squeeze is a constraint
whose failure a machine can detect; the power is not any single layer but the
*stacking*, since each eliminates a different class of defect and together they
leave very little room for a bug to hide. **This is what a `*CSL` is** — not a
prover bolted onto a language, but a discipline that squeezes from every side.

The layers split into the **cornerstone (S0)**, which squeezes the *specification*,
and the **mechanical gates (S1–S9)**, which squeeze the *implementation* until it
satisfies that spec.

| # | Layer | What it squeezes | Gate |
|---|---|---|---|
| **S0** | [source of truth](source-of-truth.md) (English norm + reference impl.) | the **spec itself** — pinned between what is *specified* and what *executes*; no freedom between them | contract reviewed vs the English reference **and** a concrete test vs the reference implementation; a norm↔impl disagreement is a finding, not a free choice |
| S1 | CSL contracts (`requires`/`ensures`) | the code must satisfy the spec | SMT solver via Why3 |
| S2 | formal semantics (Rocq + Lean) | WP calculus ↔ operational semantics agree | proof assistant (`Qed`) |
| S3 | reference tests + traceability | every construct has a passing test; verdicts never regress | CI gate |
| S4 | self-annotation | the verifier satisfies its own contracts | the verifier verifying itself |
| S5 | dual-prover anchoring | two kernels accept the same theorems | cross-check script |
| S6 | IR schema validation | the Module 5 → 6 boundary is machine-checkable | schema validator |
| S7 | TCB tier inventory | every trust assumption is named and tracked | `Print Assumptions` audit |
| S8 | real-world test cases | contracts are expressible for actual programs | self-annotation + stdlib + production code |
| S9 | auto-trust tracking | every escape hatch is a tracked bug | auto-trust count in CI |

---

## S0 is the cornerstone

S1–S9 are worthless on a spec that was never pinned to the
[source of truth](source-of-truth.md). S0 decides what the spec must *say*
(squeezed between the English norm and the reference implementation); S1–S9 then
squeeze the implementation until it provably says it. S0 is therefore the **first
step of [extreme rigor](extreme-rigor.md)**, applied before any loop invariant or
`\trusted` decision.

S0 differs in *kind* from S1–S9: it is a per-spec **authoring and review**
discipline (fidelity of each contract to the norm and the reference
implementation), not a single mechanical CI gate owned by one System. That is why
the project-level *per-Squeeze coverage* checks (`project-lifecycle`,
`cmmi-coherency-audit` C8) enumerate the System-owned gates **S1–S9** and do not
assign S0 a System owner — S0 is everyone's first step, enforced by review and the
reference corpus.

Fuller statement: `config/skills/csl-from-scratch/SKILL.md` §0.5;
`config/skills/csl-philosophy/SKILL.md` "The source of truth".

---

## Related terms

- [source of truth](source-of-truth.md)
- [extreme rigor](extreme-rigor.md)
- [backend-as-enforcer](backend-as-enforcer.md)
- [reference test](reference-test.md)
- [emission-identical gate](emission-identical-gate.md)

> **In short:** stack constraint layers so only correct code survives; S0 (the
> source-of-truth squeeze) pins the spec, S1–S9 pin the implementation, and the
> more you stack the less room a bug has to hide.
