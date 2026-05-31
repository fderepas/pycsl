# BL — Business Level Specification (PyCSL)

**Document ID:** SPEC-PYCSL-BL-001
**Profile:** P
**Status:** Active
**Effective date:** 2026-05-31
**Layer:** L1 (Business)
**Project:** PyCSL

---

## Charter (PyCSL-instance preamble)

Generate a formally proven annotation system for Python with the
smallest possible Trusted Code Base (TCB). PyCSL is the reference
implementation of the `*CSL` family — any pattern proven here should
transfer to GoCSL, ccsl, cppcsl, rustcsl, jscsl.

The operational playbook for *how* to build such a system is owned
by the [`csl-from-scratch`](../../../config/skills/csl-from-scratch/SKILL.md)
skill. **That skill IS this BL plan.** This file is a pointer, not
new prose. The PyCSL-specific framing is:

- Host language: Python 3.10+
- Contract syntax: `#@` comment annotations
- Verifier output: WhyML (`.mlw`) for Why3
- Dual-prover anchoring: Rocq (`.v`) + Lean 4 (`.lean`)
- Reference docs: `README.md`, `docs/pycsl-{concrete-syntax,static-semantics,translational}-reference.md`
- Test corpus: `test-suite/corpus/pycsl-reference/`

---

## BL plan include

<!-- pycsl-include: source=config/skills/csl-from-scratch/SKILL.md scope=L1-BL-plan -->

The `csl-from-scratch` skill defines:
- Phases 0–10 (bootstrap, language+IR, formal semantics, trust discipline)
- §0.5 Squeeze Strategy S1–S9 (the BL requirements set)
- §1 Success criteria for a *CSL build
- §14 Anti-patterns
- §17 References (trust chain, formal-semantics worked examples)

Resolve this include with `bin/cmmi-include-expand.py
projects/pycsl/BL/specifications/main.md` to view the inlined
playbook. Verify with `bin/cmmi-include-expand.py --verify
projects/pycsl/BL/specifications/main.md`.

---

## BL → System decomposition

Every BL requirement (Squeeze S1–S9 from csl-from-scratch §0.5) must
be owned by at least one System. Every non-glue System must own at
least one Squeeze. The `cmmi-coherency-audit` C8 step 5 enforces
this invariant.

| Squeeze | Constraint (BL requirement) | Owning System(s) |
|---|---|---|
| **S1** | CSL contracts (`requires`/`ensures`) — code satisfies the spec | SY3-Pycsl (parser, Module6 emission), SY6-PycslLib (stdlib stubs) |
| **S2** | Formal semantics (Rocq + Lean) — WP calculus agrees with operational semantics | SY1-FormalSemantics |
| **S3** | Reference tests + traceability matrix — every grammar production has a passing test | SY3-Pycsl (`test-suite/`, `traceability-pycsl.md`) |
| **S4** | Self-annotation — verifier satisfies its own contracts | SY8-SelfAnnotate |
| **S5** | Dual-prover anchoring — two kernels accept the same theorems | SY2-Lean2Pycsl + SY7-Rocq2Pycsl + `bin/check-proof-crosscheck.sh` |
| **S6** | IR schema validation — Module 5 → Module 6 boundary is machine-checkable | SY3-Pycsl (`src/pycsl/ir_schema.py`) |
| **S7** | TCB tier inventory — every trust assumption is named, tiered, tracked | SY1-FormalSemantics + cross-cutting |
| **S8** | Real-world test cases — contracts expressible on real programs | SY6-PycslLib, SY8-SelfAnnotate |
| **S9** | Auto-trust tracking — every escape hatch is a tracked bug | SY3-Pycsl (auto-trust counter), SY5-PycslEmit |

**Glue Systems** (no Squeeze directly):
- **SY4-PyCSLBridge** — translates between SY1/SY2/SY7 (formal
  semantics ↔ Lean ↔ Rocq); declared in `PROJECT.md` `glue_systems:`.

---

## Acceptance criteria

A PyCSL build is "BL-complete" when:

1. **S2 squeeze proves at scale.** `Print Assumptions` on the
   soundness theorem returns ≤ 2 axioms (the irreducible
   `why3_certificate` + `module6_encodes_mlw`).
2. **S5 squeeze converges.** `bin/check-proof-crosscheck.sh`
   reports zero unreconciled pairs across the Rocq/Lean registry.
3. **S4 squeeze closes the loop.** `bin/run-self-annotation-suite.sh`
   passes for every module in `src/pycsl/` (currently:
   `errors.py` only; growth criteria in `pycsl-stdlib-coverage` §9).
4. **S9 squeeze trends down.** Auto-trust count per release is
   monotonically non-increasing.

These are long-arc criteria — full BL completion is a multi-year
program per `csl-from-scratch` §15. Per-System acceptance criteria
appear in each `BL/SY<N>-<Name>/specifications/main.md`.

---

## Cross-cutting strategy

| Strategy | csl-from-scratch §  | PyCSL anchor |
|---|---|---|
| Squeeze stacking | §0.5 | `bin/cmmi-audit.sh` composes all gates |
| Prior-art study | Phase 0 | `docs/prior-art.md` (Frama-C, Creusot, Dafny, F*) |
| 6-module pipeline | Phases 1-3 | `src/pycsl/Module{1..6}_*.py` |
| Language + IR reference | Phases 4-5 | `docs/pycsl-{concrete,static,translational}-reference.md` |
| Formal semantics | Phase 6 | SY1-FormalSemantics |
| TCB reduction loop | Phases 7-10 | quarterly `Print Assumptions` audit |

---

## Verification

The BL spec passes verification when:

1. `bin/cmmi-include-expand.py --verify
   projects/pycsl/BL/specifications/main.md` reports 0 broken includes.
2. `bin/cmmi-audit.sh` C8 step 5 reports Squeeze coverage complete
   (every S1–S9 has ≥1 owner; every non-glue System owns ≥1 Squeeze).
3. Every System listed in the decomposition table has a corresponding
   `projects/pycsl/BL/SY<N>-<Name>/` directory.

---

## References

- [`config/skills/csl-from-scratch/SKILL.md`](../../../config/skills/csl-from-scratch/SKILL.md) — the BL operational playbook (the source of truth this file points at).
- [`config/skills/csl-philosophy/SKILL.md`](../../../config/skills/csl-philosophy/SKILL.md) — the family thesis csl-from-scratch operationalizes.
- [`README.md`](../../../README.md) — PyCSL-instance user-facing overview.
- [`PROJECT.md`](../../PROJECT.md) — project charter with the full 9-system inventory + Squeeze ownership block.
- [`cmmi-tailoring-plan.md`](../../../cmmi-tailoring-plan.md) — how the BL → System mapping was derived and the verification gates that enforce it.
