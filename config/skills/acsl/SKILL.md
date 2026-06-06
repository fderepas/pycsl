---
name: acsl
description: >-
  Reference for writing, reading, and debugging formal specifications of C
  in ACSL (the ANSI/ISO C Specification Language) and MetAcsl (its high-level
  meta-property extension), verified with Frama-C. Use whenever the task involves
  ACSL annotations (requires/ensures/assigns, loop invariants/variants,
  predicates, lemmas, axiomatics, ghost code, \valid, \separated, behaviors),
  MetAcsl meta-properties / HILAREs (\writing and \reading contexts,
  \written/\read meta-variables, integrity or confidentiality properties spanning
  many functions), Frama-C plug-ins (WP, Eva, E-ACSL, RTE), deductive
  verification of C, runtime assertion checking, proving safety or security
  properties of C, or interpreting Frama-C proof failures. Trigger even when the
  user only shows a C file with /*@ ... */ comments and asks to verify, prove,
  annotate, add a contract or loop invariant, or asks "why won't this prove" —
  and whenever they mention Frama-C, ACSL, MetAcsl, WP, weakest precondition,
  proof obligations, or EAL certification of C.
---

# ACSL & MetAcsl for Frama-C

This skill is a working reference for specifying and verifying C programs with
**ACSL** (the behavioral specification language) and **MetAcsl** (the extension
for pervasive, high-level "meta-properties"), both checked by the **Frama-C**
platform.

The body below gives the conceptual map, a quick-reference cheat sheet, the
verification workflow, and the common failure-debugging playbook. For exhaustive
construct-by-construct detail, load the reference files named in each section —
do not try to recall syntax from memory when a reference file covers it, because
the exact spelling of clauses, predicates, and contexts is where mistakes happen.

## Mental model

ACSL is a **contract language**: each function gets a precondition, a
postcondition, and a frame condition (what it may modify). Frama-C's **WP**
plug-in compiles these into proof obligations discharged by SMT solvers (via
Why3). The discipline is *modular*: each function is proved in isolation,
trusting only the contracts of its callees.

MetAcsl sits *above* ordinary contracts. Some properties — "no function except
`encrypt` may write a confidential page", "no read touches a higher-clearance
buffer" — are not naturally one function's contract; they are invariants over
**many program points across many functions**. MetAcsl lets you write one
**HILARE** (HIgh-Level Acsl REquirement) that it then *expands* into a large
number of ordinary ACSL assertions at every matching point, which WP/Eva/E-ACSL
then prove. So: ACSL is the base layer; MetAcsl is a macro layer that generates
ACSL.

```text
  high-level requirement          ┌─────────────┐   many ordinary
  (one HILARE)            ──────▶  │  MetAcsl     │ ─────────────────▶  ACSL assertions
  e.g. "no leak of secret"        │  (-meta)     │   (one per write/read site)
                                  └─────────────┘
                                                         │
  function contracts (ACSL)  ────────────────────────────┤
                                                         ▼
                                          ┌──────────────────────────┐
                                          │ WP (proof) · Eva (AI) ·   │
                                          │ E-ACSL (runtime) · RTE    │
                                          └──────────────────────────┘
```

## Reference files — load these on demand

- **`references/acsl-reference.md`** — Exhaustive ACSL: annotation syntax,
  function contracts (requires/ensures/assigns/allocates/frees/terminates/
  decreases, behaviors, complete & disjoint), abrupt-termination clauses,
  statement annotations (assert/check/admit, ghost code, statement contracts),
  loop annotations (invariant/assigns/variant), the logic language (predicate,
  logic, lemma, axiomatic+axiom, inductive, type, \let), built-in memory
  predicates (\valid, \valid_read, \separated, \initialized, \fresh,
  \block_length, \base_addr, \offset, \dangling), labels and \at/\old/\result,
  logic types (integer, real, boolean, sets, ranges), and data invariants.
  **Read this whenever you write or read any /*@ ... */ contract.**

- **`references/metacsl-reference.md`** — Exhaustive MetAcsl: the HILARE model
  (target / context / property), the four contexts (weak_invariant,
  strong_invariant, \writing, \reading) and their meta-variables (\written,
  \read), the documented concrete syntax and how it has evolved across releases,
  the transformation semantics (how each context becomes pre/post/assertions),
  why \writing beats `assigns` for non-transitive and conditional restrictions,
  the CLI (`-meta`), backends, and installation. **Read this for any
  meta-property, integrity, confidentiality, or "property over many functions"
  task.**

- **`references/patterns-and-examples.md`** — Worked, copy-adaptable examples:
  array algorithms with loop invariants/variants, predicate + axiomatic
  definitions (sortedness, permutation), multi-behavior contracts, ghost-code
  proof witnesses, and complete MetAcsl integrity/confidentiality specs.
  **Read this when you need a concrete template to adapt.**

- **`references/bibliography.md`** — Annotated primary sources: the ACSL manual,
  the Frama-C/WP manuals, *ACSL by Example*, the MetAcsl papers, the
  *Guide to Software Verification with Frama-C* book, and real-world case studies
  (JavaCard VM EAL6, Contiki, Linux kernel, hypervisors, aerospace). **Read this
  when the user wants sources, further reading, or real-life example corpora.**

## Verification workflow

Follow this order; it mirrors how practitioners actually converge on a proof.

1. **Pick the backend for the goal.** Deductive proof of functional correctness
   → **WP**. Absence of runtime errors over the whole reachable state space →
   **Eva** (abstract interpretation). Checking annotations dynamically on real
   executions → **E-ACSL** (instruments the code). Pervasive cross-cutting
   property → **MetAcsl** to generate annotations, then WP or E-ACSL to discharge
   them.

2. **Generate runtime-error guards first.** Run the **RTE** plug-in (or
   `-wp-rte`) so WP must also prove no overflow, no invalid pointer, no division
   by zero, etc. Functional contracts that ignore RTE are usually unsound in
   practice.

3. **Specify before implementing the proof.** Write `requires`/`ensures`/
   `assigns` for every function. `assigns` is mandatory for sound modular proof —
   an omitted or wrong frame clause is the single most common cause of both false
   proofs and unprovable callers.

4. **Annotate loops.** Every loop needs a `loop invariant` (inductive: holds on
   entry and is preserved), a `loop assigns` (what the loop body may modify), and
   a `loop variant` (a non-negative integer expression that strictly decreases,
   to prove termination). See the loop section of the ACSL reference.

5. **Strengthen with the logic layer when SMT stalls.** Factor hard reasoning
   into `predicate`/`logic` definitions and `lemma`s; prove lemmas separately
   (sometimes interactively in Coq/Why3). Use `axiomatic` blocks for recursive
   logic definitions, and **lemma functions / ghost code** to give the prover an
   explicit witness.

6. **Iterate on failures** using the playbook below.

7. **Re-run after every code change** — especially for MetAcsl properties, whose
   whole point is to be cheaply re-verified after edits so an implicit security
   property cannot silently break.

## Debugging proof failures — playbook

When WP reports an unproved goal, diagnose in this order:

- **Missing/insufficient loop invariant.** The goal mentions a loop. The
  invariant is probably not *inductive* (true on entry but not preserved), or
  too weak to imply the postcondition. Strengthen it; add the bounds the body
  relies on.
- **Frame problem (`assigns`).** A caller can't prove a property it "obviously"
  keeps, because a callee's `assigns` is too permissive (or missing, defaulting
  to "may modify everything"). Tighten callee `assigns`, add `\from`.
- **Aliasing / separation.** Pointer arguments may overlap. Add
  `requires \separated(...)` or `\valid` ranges; WP's typed memory model is
  sensitive to this.
- **Integer vs. machine arithmetic.** ACSL `integer` is unbounded; C `int`
  overflows. A goal fails because the spec is stated in mathematical integers
  but RTE demands no overflow. Add range `requires`, or model with explicit
  casts.
- **Nonlinear / quantified goals the SMT solver can't close.** Introduce a
  `lemma`, or a ghost computation, or split the `behavior`s. Try alternate
  provers (Alt-Ergo, Z3, CVC5) via Why3.
- **MetAcsl: a generated assertion fails.** MetAcsl points you to the exact site
  (e.g. a specific write) and the instantiated meta-variable (e.g. `\written`
  replaced by `fp->level`). Treat it as an ordinary ACSL failure at that site —
  often the fix is reordering statements or adding a guard, as in the canonical
  confidentiality example in the MetAcsl reference.

## House rules for produced annotations

- Always state `assigns` for every function and `loop assigns` for every loop;
  never leave them implicit.
- Prefer `integer`/`real` in the logic and constrain machine ranges with
  explicit `requires`, rather than silently mixing C and mathematical types.
- Keep one idea per `behavior`; use `complete behaviors;`/`disjoint behaviors;`
  to make case analyses checkable.
- Define reusable notions as `predicate`/`logic` rather than copy-pasting
  formulae; it makes both proofs and reviews tractable.
- For a property that must hold at *many* points or across *many* functions,
  reach for a MetAcsl HILARE instead of hand-writing repeated assertions.
- Do not invent ACSL or MetAcsl syntax. If unsure of a clause or predicate
  spelling, consult the relevant reference file in this skill before writing.
