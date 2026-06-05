---
name: csl-from-scratch
description: Operational playbook for building a fresh *CSL deductive verifier
  for any host language, from first prototype through formal semantics and
  TCB reduction. Use when bootstrapping ccsl/gocsl/jscsl/rustcsl/cppcsl or any
  new family member; complements csl-philosophy (the thesis) and pycsl-how-to-develop
  (the Python-specific tactical guide). Covers Phase 0 prior-art study, the
  6-module compiler pattern, dual-prover anchoring via Rocq + Lean,
  self-annotation, memory models, the auto-trust safety valve, and the
  long-term trust-reduction discipline. Python and PyCSL are referenced as
  illustrative examples; the methodology is language-agnostic.
---

# Building a *CSL from scratch

Operational playbook for constructing a new *CSL deductive verifier
(`<lang>csl`) for any host language. Reads as a sequenced
playbook — phases run in roughly the listed order, though several
overlap once the prototype is alive.

`*CSL` is the family name: PyCSL for Python, ccsl for C, gocsl for
Go, jscsl for TypeScript, rustcsl for Rust, cppcsl for C++. The
philosophy of the family is in
[`config/skills/csl-philosophy/SKILL.md`](../csl-philosophy/SKILL.md);
this skill is the *operational counterpart*. It assumes you've
read csl-philosophy and now want to ship code.

Python and PyCSL appear throughout as worked examples. Treat them
as the reference *implementation* of the playbook; substitute
your host language wherever this skill says "Python".

---

## 0. The methodology in one paragraph

Start by prototyping the slice of the host language you already
know how to verify, with a minimal `#@`-style contract surface
borrowed from prior art. Then iterate: capture host-language
shape via a traceability matrix that drives the reference test
corpus; capture *CSL annotation-language shape via a written
reference guide that drives more tests; refactor between phases
into a stable 6-module pipeline; eventually formalize the IR and
WP calculus in a proof assistant; then reduce the TCB by
replacing trust assumptions with mechanical checks — a multi-year
arc that's never "done" but reaches well-defined stable
intermediate states (zero PyCSL-specific axioms; mechanical
cross-prover diff; self-annotation under full proof).

Every phase applies the same meta-principle — the **Squeeze
Strategy** (§0.5): stack constraint layers with mechanical
gates so that only correct implementations survive all checks.

---

## 0.5 The Squeeze Strategy

Every phase of this playbook applies the same meta-principle:
**squeeze the implementation space until only correct code
survives**. A *squeeze* is a constraint layer with a
mechanical gate — a check that a machine can run, whose
failure means the implementation violates the constraint.

The power of the *CSL methodology is not any single technique
but the *stacking* of squeezes. Each layer eliminates a
different class of defect. Together they leave very little room
for a bug to hide.

### Squeeze layers

| # | Layer | What it constrains | Mechanical gate |
|---|---|---|---|
| S1 | **CSL contracts** (`requires`/`ensures`) | The developer (or agent) must write code that satisfies the spec | SMT solver via Why3 |
| S2 | **Formal semantics** (Rocq + Lean) | The WP calculus and operational semantics must agree | Proof assistant (`Qed`, `theorem`) |
| S3 | **Reference tests + traceability matrix** | Every grammar production has a passing test; verdicts never regress | CI gate (`make test`; verdict-drift = hard fail) |
| S4 | **Self-annotation** | The verifier's own implementation must satisfy its own contracts | The verifier verifying itself |
| S5 | **Dual-prover anchoring** | Two independent proof kernels must accept the same theorem statements | Cross-check script (`bin/cross-check-provers.sh`) |
| S6 | **IR schema validation** | The Module 5 → Module 6 boundary has a machine-checkable contract | Schema validator (`ValidateIR` / `validate_ir`) |
| S7 | **TCB tier inventory** | Every trust assumption is named, tiered, and tracked | `Print Assumptions` audit |
| S8 | **Real-world test cases** | Contracts must be expressible for actual programs, not just toy examples | Self-annotation + stdlib stubs + production code |
| S9 | **Auto-trust tracking** | Every "escape hatch" is a tracked bug, not permanent policy | Auto-trust count reported in CI |

### How the squeezes compose

```
┌─────────────────────────────────────────────────────┐
│ S9  Auto-trust count ≤ N                           │
│ ┌─────────────────────────────────────────────────┐ │
│ │ S8  Real-world code verifies                    │ │
│ │ ┌─────────────────────────────────────────────┐ │ │
│ │ │ S7  Print Assumptions = ∅ (zero axioms)     │ │ │
│ │ │ ┌─────────────────────────────────────────┐ │ │ │
│ │ │ │ S5+S6  Dual provers agree + IR schema   │ │ │ │
│ │ │ │ ┌─────────────────────────────────────┐ │ │ │ │
│ │ │ │ │ S4  Self-annotation passes          │ │ │ │ │
│ │ │ │ │ ┌─────────────────────────────────┐ │ │ │ │ │
│ │ │ │ │ │ S3  127/127 tests pass          │ │ │ │ │ │
│ │ │ │ │ │ ┌─────────────────────────────┐ │ │ │ │ │ │
│ │ │ │ │ │ │ S1  SMT proves the VCs      │ │ │ │ │ │ │
│ │ │ │ │ │ │ ┌─────────────────────────┐ │ │ │ │ │ │ │
│ │ │ │ │ │ │ │ S2  Soundness Qed       │ │ │ │ │ │ │ │
│ │ │ │ │ │ │ └─────────────────────────┘ │ │ │ │ │ │ │
│ │ │ │ │ │ └─────────────────────────────┘ │ │ │ │ │ │
│ │ │ │ │ └─────────────────────────────────┘ │ │ │ │ │
│ │ │ │ └─────────────────────────────────────┘ │ │ │ │
│ │ │ └─────────────────────────────────────────┘ │ │ │
│ │ └─────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

Read the diagram inside-out: the soundness theorem is the
bedrock; everything else is layered atop it. SMT discharges
VCs *because* the WP calculus is proven sound, not the other
way around — without S2, S1 is operating on unjustified rules.
Tests (S3) confirm the implementation matches the model that
S1 reasons about; self-annotation (S4) confirms the verifier
verifies itself; dual provers (S5+S6) confirm two independent
kernels agree; zero-axiom (S7) confirms no hidden trust;
real-world code (S8) confirms it scales; auto-trust (S9)
confirms escape hatches stay bounded.

Each ring eliminates defects that could pass through all inner
rings. S1 alone stops logic bugs in a single program; but an
incorrect WP calculus could make S1 vacuously true — S2
squeezes that out. S3 and S6 catch drift between the
formalization and the implementation. S4–S9 then add
progressively rarer audit perimeters.

A note on S1 ↔ S2 ordering. S1 (SMT solver) and S2 (theorem
prover) check *different* properties: S1 asks "does the
developer's spec hold for this program?"; S2 asks "are the
proof rules sound at all?". The nesting captures **trust depth**
(S2 is the foundation S1 stands on), not strict execution
precedence. In practice S1 runs in seconds per file while S2
is a one-time, kernel-checked theorem — they live at different
cadences but the trust chain runs S2 → S1, not the reverse.

### The AI-agent implication

When an AI agent works inside a *CSL codebase, each squeeze
layer is a **strict perimeter** the agent cannot cross without
being caught:

- An agent writing Go code is squeezed by `//@` contracts —
  Why3 rejects wrong implementations.
- An agent writing annotations is squeezed by the SMT solver —
  invalid specs fail proof.
- An agent modifying formal semantics is squeezed by `coqc` /
  `lake build` — type errors and proof failures stop drift.
- An agent refactoring Module 6 is squeezed by the reference
  corpus — verdict regression fails CI.

**The more squeezes you stack, the less room an agent has to
produce incorrect output that passes all gates.** This is what
makes *CSL codebases unusually safe for AI-assisted
development: the perimeter is mechanically enforced, not
review-dependent.

---

## 1. Premise and success criteria

A *CSL is built when:

1. **Annotation surface**: the host language admits `#@` (or
   `//@`, `/// @`, `@verify`, …) annotation comments carrying a
   contract language with `requires`, `ensures`, frame
   conditions (`assigns`), loop invariants + variants, and
   `\result` / `\old` operators.
2. **Verification pipeline**: a CLI `<lang>csl <file>` parses
   the annotated file, emits Why3 (`.mlw`), dispatches to Why3,
   prints a verdict. Exit code 0 on full proof; non-zero on any
   unproven VC.
3. **Proof-assistant anchoring**: directives like
   `#@ proof rocq <qualname>` import Why3 axioms whose
   evidence lives in companion `.v` / `.lean` files;
   mechanical cross-check binds the registry to the cited
   theorems (no manual review trust seam).
4. **Self-annotation**: the verifier annotates its own
   implementation; the suite runs under full proof on every CI.
5. **TCB story**: explicit per-tier inventory of trust
   assumptions, with each non-Tier-0 entry mapped to a planned
   replacement step.

Pick a worked example function and verify it end-to-end at
**Phase 1** (Euclidean GCD is the canonical choice — see
[`0342_explanation.md`](../../../0342_explanation.md) for the
PyCSL execution).

---

## 1.5 Extreme rigor — the bar for high-touch work

Baseline annotation lets the bar sit wherever it lands.
**Extreme rigor (ER)** is the standard for code where wrong
contracts cost trust: the formal-semantics layer, load-bearing
framework files, and — most visibly — the standard library
annotation pass.

The canonical worked example is `unix-filesystem/UnixInodeFileSystem.py`
in this repository: 666 lines modelling a Unix-like inode
filesystem, with Coq-anchored bitwise lemmas, loop invariants
*and* variants on every loop, round-trip axioms for inverse
operation pairs, and each remaining `\trusted` paired with a
named feature-plan gap. Read it before you touch the stdlib.

The five habits that distinguish ER from baseline annotation:

1. **Loop invariants AND variants on every loop.** Either alone
   leaves the prover guessing. Variant proves termination;
   invariant proves the loop's contribution to the
   postcondition.
2. **Body verification first; `\trusted` only with a cited
   blocker.** The default annotation effort targets a
   body-verified function. `\trusted reviewer:` is acceptable
   *only* when you can name what blocks promotion — typically a
   missing IR feature, tracked in a `missing-*-feature.md` plan.
3. **Coq/Lean axioms for facts SMT cannot discharge.** When Z3
   times out on a bitwise property (the `_get_bitmap`
   `(x >> y) & 1 ∈ {0, 1}` pattern blew up at ~3.4B steps), the
   move is `#@ proof rocq <qualname>` importing a kernel-checked
   theorem as a Why3 preamble axiom. Z3 then dispatches it in
   zero steps. The Coq theorem lives in the companion
   `.proofs/rocq/` directory.
4. **Round-trip axioms for inverse operation pairs.** Pack/unpack,
   encode/decode, serialize/deserialize — when the inverse is
   semantically guaranteed but operationally abstract, declare a
   round-trip axiom (`unpack(pack(...)) = ...`) anchored in a
   witness Coq module that proves it by `reflexivity` on a
   concrete model. See `unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v`,
   `Module UnixFs.Struct.Fmt_i1a1`.
5. **Each `\trusted` carries an actionable `cite:_note:`.** Not
   "Module 6 limitation" — name the precise IR-emission gap
   (e.g., "dict-literal in return value", "tuple-subscript on
   struct_unpack returns") *and* the feature plan that tracks
   the gap. Without that, `\trusted` becomes permanent.

ER work is supposed to expose IR-feature gaps. The
UnixInodeFileSystem pass surfaced six, catalogued in
`missing-pycsl-ir-features.md`. That's a feature, not a bug —
ER drives the language forward by refusing to silently absorb
limitations.

This is the standard the standard-library annotation pass must
meet. See [`references/stdlib-extreme-rigor.md`](references/stdlib-extreme-rigor.md)
for the case study, the acceptance checklist, and the
escalation ladder for when body verification fails.

The supervisor-side enforcement of ER lives in
[`feature-supervisor-extreme-rigor.md`](../../../feature-supervisor-extreme-rigor.md)
at repo root — phases carry `**Acceptance:**` blocks that the
supervisor executes and reports on; "done" is no longer
self-declared.

---

## Phase reference files

The detailed playbook for each phase lives in `references/`.
Load the file that matches what you're about to do:

- **[`references/phases-bootstrap.md`](references/phases-bootstrap.md)**
  — Phases 0-3: prior-art study, MVP prototype, host-grammar
  traceability matrix, the 6-module refactor. Load when
  scaffolding a fresh family member or revisiting an
  early-stage architectural decision.

- **[`references/phases-language-and-ir.md`](references/phases-language-and-ir.md)**
  — Phases 4-5: *CSL annotation-language reference + the
  second IR-tightening refactor. Load when designing the
  contract surface or hardening the Module 5↔6 boundary.

- **[`references/phase-formal-semantics.md`](references/phase-formal-semantics.md)**
  — Phase 6: Rocq+Lean formalization, soundness proof order,
  forward-vs-backward reasoning, bug-discovery examples,
  abstraction gaps, Lean DecidableEq workaround, instance
  citation gotchas. Load when starting the proof-assistant
  work or when stuck on a soundness/correspondence proof.

- **[`references/phases-trust-discipline.md`](references/phases-trust-discipline.md)**
  — Phases 7-10: TCB reduction loop, self-annotation,
  stdlib + memory models + third-party stubs + real-world
  application verification, continuous-trust-reduction CI
  gates, auto-emit + drift-aware registry merge. Load when
  doing quarterly TCB work or wiring CI for the long-term
  trust gate.

- **[`references/cross-cutting-concerns.md`](references/cross-cutting-concerns.md)**
  — Annotation-vs-proof gap, auto-trust safety valve, reference
  test discipline (numbering, never-renumber), skills+RAG, the
  Layer terminology, TCB tier glossary. Load when navigating
  a boundary question that spans multiple phases.

- **[`references/anti-patterns.md`](references/anti-patterns.md)**
  — the full anti-patterns checklist (formal-semantics
  ordering, naming, sugar-vs-IR, extraction freshness, deferred
  plans, acceptance-claim gaming, soundness-proof tactics).
  Load when reviewing a design choice or before committing a
  phase, to confirm you're not falling into a known trap.

- **[`references/further-reading.md`](references/further-reading.md)**
  — the full reference index: family skills, formal-semantics
  worked examples, architectural docs, operational references,
  reference test corpus, external prior art, and the
  end-to-end gocsl trust chain. Load when you need a specific
  pointer or the proven trust-chain shape.

---

## 15. Suggested first-week deliverables

For a fresh `<lang>csl` clone:

| Day | Deliverable |
|---|---|
| 1-2 | Prior-art notes (`docs/prior-art.md`) + minimal prototype (Phase 1). |
| 3   | 5-10 reference tests with traceability matrix. |
| 4-5 | Module 1-3 split + Module 4 stub. |
| EOW | `<lang>csl gcd.<ext>` verifies under SMT, end-to-end. |

That's the spike. Real coverage takes quarters; this is just
the proof that the architecture flies.

After Week 1: Phase 2 (host-language traceability fill-in), then
Phase 3 (Module 6 build-out), then language reference (Phase 4)
— each runs ~4-8 weeks. Phase 6 (formal semantics) and beyond
are multi-quarter.

---

## 16. The discipline summary

If you remember nothing else from this skill:

0. **The Squeeze Strategy is the meta-principle.** Every phase
   adds a constraint layer with a mechanical gate. Stack enough
   squeezes and only correct implementations survive all checks.
   When delegating to agents, each squeeze defines a strict
   perimeter the agent cannot cross without being caught.
1. **Single sentence per phase**: do the smallest end-to-end
   thing that flies; then expand by traceability.
2. **Mechanical checks beat manual review.** Every trust seam
   that can be mechanically checked, should be.
3. **Two provers beat one.** Cross-prover disagreement is the
   cheapest soundness signal available.
4. **Self-annotation is a hard requirement.** A *CSL that can't
   verify itself is incomplete.
5. **TCB reduction is the long game.** Plan for quarters, not
   sprints.
6. **Proof attempts find bugs.** Expect 2-5 semantic bugs to
   surface during the soundness proof that no testing catches.
   These are *relationships between functions* (eval↔wp, wp↔gen)
   that only break when you try to prove they agree. This is
   the highest-value activity in the formal semantics phase.
7. **Forward reasoning for soundness.** Use
   `exact (IH pre_es _ _ _ _ _ Hwp)`, not
   `apply IH. exact Hwp.` Coq can't infer record-state
   parameters when `outcome_satisfies` is a `Definition`.
8. **Track Admitted count per build.** Report it automatically
   (`grep Admitted | wc -l`). The count should monotonically
   decrease. Any increase must be justified.
9. **Grow the surface by desugaring, not by growing the TCB.** A new
   annotation form that is expressible over existing primitives is added
   as *sugar* — a parser rule + a weaver desugaring pass that lowers it to
   those primitives — with **zero** new IR/backend/trusted surface. Verify
   what each target primitive actually *proves / assumes / drops* before
   lowering onto it; contain the front-end change so non-sugar inputs stay
   byte-identical; and give the sugar a negative test so it has teeth. Sugar
   buys ergonomics, not proving power — so spend it only where the
   ergonomic gain (e.g. DRY) is real. See Phase 4b in
   `references/phases-language-and-ir.md`.
10. **Whole-program meta-properties expand to per-site obligations — and their
    soundness is a theorem you write down first.** One module-level requirement
    (PyCSL's HAPPY) synthesizes many ordinary per-site `#@ check`s — desugaring
    at *program* scope, reusing a statement-level primitive with zero new TCB.
    What makes per-site expansion sound *without* alias/effect analysis: state
    each obligation at the **location actually written** (not a syntactic name),
    and inject at **every** body's own write sites so indirect/callee writes are
    caught at the callee — **universal coverage replaces the call graph**; the
    only residual gap is bodyless functions, closed by a *synthesized* effect
    declaration at the trust boundary (never a pattern-matched hand-written one).
    Naïve "enumerate writes to the name" is the unsound trap. A meta-feature can
    bottom out on a missing real primitive (Phase 4b item 1, recursively) — and
    it surfaces under-specified methods, which you report honestly rather than
    fake a proof for. See Phase 4c in `references/phases-language-and-ir.md`.

---

## 17. References

See [`references/further-reading.md`](references/further-reading.md)
for the full reference index — family skills, formal-semantics
worked examples, architectural docs, operational references,
reference test corpus, external prior art, and the end-to-end
gocsl trust chain.
