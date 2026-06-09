---
name: csl-philosophy
description: Internalize the design philosophy of the *CSL family (PyCSL, ccsl, gocsl, jscsl, rustcsl, cppcsl) — deductive verifiers built around proof-assistant-sourced specifications, Why3 as a shared backend, and Rocq+Lean cross-validation. Use this skill whenever the user is designing, extending, contributing to, or making architectural decisions about any tool in this family, including discussions about `proof` directives, `proof2why3`, spec bridges between proof assistants and source-language contracts, ACSL/Pearlite/PyCSL-style annotation languages, or how to integrate proof-assistant theorems into deductive verifiers. Trigger generously — questions about WhyML emission, how to formalize a function's contract, whether to verify in Rocq vs annotate in source, where to put a new spec, or how to make a verifier "feel right" all need this philosophical grounding before tactical answers will land correctly.
---

# *CSL philosophy

A guide for any agent working on the *CSL family of deductive verifiers
(PyCSL for Python, ccsl for C, gocsl for Go, jscsl for TypeScript,
rustcsl for Rust, cppcsl for C++). These tools share a philosophy
that is unusual in the verification landscape, and getting tactical
advice right depends on having the philosophy right first.

## The thesis in one paragraph

A function's specification has at most one true source. If a property
has been proven in a proof assistant, the proof is the specification.
Contracts in the source file are projections of that specification onto
a syntax the programmer can read. Why3 axioms emitted to the SMT layer
are projections of the same specification onto a syntax the solver can
chew on. Three surfaces, one underlying object. The toolchain's job is
to make these projections faithful, mechanical, and auditable — and to
refuse to ship when they disagree.

## What this means in practice

Most verification systems embed one language inside another. VST embeds
C-program reasoning inside Coq. CFML does the same for OCaml. RustBelt
puts Rust inside Iris. These are substantial intellectual achievements
and they are emphatically **not** the *CSL approach.

The *CSL approach is the opposite: **let each system speak its own
language, and bridge by reference.** Rocq users write normal Rocq. Lean
users write normal Lean. Python users write normal Python with
PyCSL annotations. C users write C with ACSL-style comments. None of
these files knows anything about the others. They are connected only
by a shared namespacing convention and a small extraction tool.

A Rocq theorem `Pycsl.Reference.Gcd.gcd_step` is the same fact as a
Lean theorem `Pycsl.Reference.Gcd.gcd_step` cited from Python as
`#@ proof rocq Pycsl.Reference.Gcd.gcd_step`. The qualified name is
the actual identifier in each system. No translation table. No central
registry. The directory structure of the proofs *is* the index.

## The source of truth: it lives outside the toolchain

The thesis above is about the *internal* single source — the proof,
projected onto three surfaces the toolchain keeps consistent. But what
decides whether those projections are *correct in the first place*?
Correctness is not an internal property. It is fidelity to an
**external source of truth**: the host language's own authorities,
which decide what a program or library actually *means*. A *CSL is only
as trustworthy as its faithfulness to them. The source of truth has two
axes, and you need both:

- **English — the normative specification.** What behavior is
  *specified*: the contract the language promises. This is what
  contracts and `ensures` clauses should transcribe.
- **Execution — the reference implementation.** What behavior actually
  *happens*: it resolves whatever the English leaves
  implementation-defined or silent (edge cases, exact exception types,
  iteration order, boundary results), and it is the ground truth a
  runnable model must agree with.

Per family member:

| Language | English (normative) | Execution (reference impl.) |
|---|---|---|
| **Python** | the [language reference](https://docs.python.org/3/reference/index.html) + the [standard library reference](https://docs.python.org/3/library/index.html) | [CPython](https://github.com/python/cpython) |
| **C** | the ISO/ANSI C norms | GCC and LLVM/Clang |
| (gocsl, rustcsl, …) | that language's spec / memory model | its reference compiler / runtime |

**How the two axes divide labor.** Write the strongest contract the
**English** justifies (it states the *intended* behavior — see
`pycsl-stdlib-coverage`). Where the English is genuinely ambiguous or
silent, the **reference implementation** decides, and the model must
match what it actually does. Where the two *disagree*, that is a finding
to surface, not a coin to flip — the "refuse to ship on disagreement"
instinct (#7) applied outward.

This is *why* the project's hardest disciplines exist. **Faithful typing**
(no-more-int: a value lowers to its true type class, never a convenience
int) is fidelity to the language's value model. The **exception model**
(`#@ no_exception`, faithful `KeyError` on a missing dict read) is
fidelity to what the reference implementation actually raises. The
**standard library** (`pure_lib/`) is shaped end-to-end by these sources:
each stub transcribes the library reference and must behave as CPython
does. A specification that is internally consistent but unfaithful to
the source of truth is *coherent and wrong* — the worst kind of green.

**Faithfulness must be auditable, and the loop must close.** Fidelity is
not a private virtue; it has to be checkable *from the outside*. So anchor
each contract to the sentence it transcribes — a `# cite:` to the
authority's page and a `# cite:_note:` paraphrase — so any reader can trace
a contract back to the spec text it encodes (the `os` model carries one on
every syscall). Formalization does **not replace** the source of truth; it
makes a faithful, mechanically-checkable **shadow** of it, and everything
downstream stays *answerable to that text*. And the source of truth is not
only where a proof *begins* — it is where it *ends*: the **formal test**
that crowns a verified module re-states the specification's own promise
(the round-trip, the documented postcondition) over symbolic inputs and
discharges it for all of them. The proof descends from the English
authority and returns to it — see "The descent and the return" below, and
`docs/formal-filesystem.md` (`os` as the worked example).

### The Squeeze Strategy starts here, and so does ER

This is the **cornerstone of the Squeeze Strategy** (the meta-principle
of the whole methodology — `csl-from-scratch` §0.5). The later squeezes
(SMT, dual provers, IR schema, self-annotation) squeeze the
*implementation* until only code that satisfies the spec survives. But
the **first** squeeze — the one that decides what the spec must even
*say* — squeezes the **specification itself between the two sources of
truth**: the English bounds it from above (the strongest contract the
norm justifies), the reference implementation bounds it from below (what
actually executes). **Squeezed between the two, the spec has no freedom.**
There is no "convenient" or "minimal" contract to choose — the only
contract is the one both sources force. Where they leave a gap, that gap
is the only latitude you have; where they conflict, you stop and surface
it (#7).

That is what a *CSL *is*: not a prover bolted onto a language, but a
discipline that pins every specification between implementation and
English so the author has no room to be wrong. **Identifying the two
sources of truth and squeezing the spec between them is therefore the
first step of Extreme Rigor (#8)** — before a single loop invariant,
before any `\trusted` decision. Get the squeeze wrong and everything
proved on top of it is *coherent and wrong*.

## The eight design instincts

Internalize these. They generate the right answer to most tactical
questions in this project.

### 1. The proof file owes nothing to the verifier

A Rocq file in a *CSL project must be a normal Rocq file. It uses
stdlib lemmas, calls `lia` and `apply`, ends each proof with `Qed`. The
only sign it participates in a larger system is a brief comment naming
the WhyML axiom it corresponds to. If you find yourself wanting to
add tool-specific tactics, embedded DSLs, or "PyCSL-aware Rocq plugins,"
stop. That breaks the philosophy.

The same applies to Lean files, C files, Python files, and so on. Each
artifact is written in its native idiom and could be moved to a
different project without modification.

### 2. The bridge is content-free

The `proof2why3` extraction tool knows nothing about the source language
it serves. It extracts theorem statements from Rocq and Lean, normalizes
to a shared first-order IR, cross-checks for agreement, and emits Why3
axioms. That's all. Addresses flow in; axioms flow out. The same bridge
serves PyCSL, ccsl, gocsl, jscsl, and any future tool in the family.

If you find yourself adding source-language-specific logic to the
bridge, stop. The logic belongs in the host verifier, not the bridge.

### 3. The namespacing IS the standard

The most important deliverable is not the verifiers. It is the convention
that proof theorems and source-language contracts share a qualified name.
This convention makes the system navigable by humans without any tooling:
read the Python file, follow the address, find the Rocq proof in fifteen
seconds. Tools come and go; conventions outlive them.

When designing any extension, ask: does this preserve the property that
a human can navigate the system without running anything?

### 4. Two provers is the entire point

Rocq and Lean proving the same statement is not redundant. Their kernels
are independent. Their stdlibs evolved separately. Their communities
audit each other's foundational definitions from different angles. A
statement that canonicalizes to the same proposition in both has crossed
two audits, and that is a stronger guarantee than anything a single
prover offers.

If you're tempted to make `proof` work with only one prover by
default, resist. The cross-check is not a feature; it is the trust
model. Single-prover mode exists as an escape hatch, not the
intended path.

### 5. Why3 is the universal layer

The family targets Why3 specifically because Why3 already serves as the
common backend for Frama-C/WP, Creusot, Cameleer, GNATprove, and others.
The *CSL contribution rides on this existing ecosystem. Adopting `proof`
in any of these tools requires only a small directive in the source
language and a small preamble hook in the Why3 emitter. Everything else
the verifier already does continues to work unchanged.

Do not propose alternative backends (Viper, Boogie, SMT-LIB directly,
custom IRs) for new *CSL members without overwhelming reason. The
ecosystem matters more than any individual tool's preferences.

### 6. Three readers, one file

A *CSL source file must read coherently to three audiences:

- **A working programmer** reads the code and the contracts as
  English-ish English. They don't need to know what Rocq is.
- **A verification engineer** reads the loop invariants and variants
  and sees a Hoare-logic proof. They don't need to know what Lean is.
- **A formal methods researcher** reads the `proof` directives
  and knows there are real, kernel-checked proofs behind each one.

All three readings must be available in the same file. If a design
choice serves one audience at the expense of another, reconsider.

The PyCSL test 0342 (Euclidean GCD) is the canonical example. Keep it
in mind as the design target for any new verifier in the family. For
the full worked example across all three files (Python source, Rocq
proof, Lean proof), read `references/canonical-example.md`. When
designing any new feature, ask "would 0342 still read coherently to
all three audiences with this in it?"

### 7. Refuse to ship on disagreement

When `proof2why3` cross-check finds that the Rocq statement and the Lean
statement for the same qualified name canonicalize to different
propositions, the bridge halts. It does not pick a winner. It does not
warn and continue. It does not emit either axiom. The default behavior
is hard failure with a structured diff.

This is non-negotiable. Silent or soft-failure modes erode the trust
model that justifies the whole architecture. If a user wants to proceed
despite disagreement, they pass an explicit flag and accept manifest
status `disagreement` in their build.

### 8. Extreme rigor is the bar where it matters

Baseline annotation lets the bar sit wherever it lands.
**Extreme rigor (ER)** is the standard for code where wrong contracts
cost trust: the formal-semantics layer, load-bearing framework files,
and the standard-library annotation pass. ER is "body-verify what you
can; axiom-anchor what you cannot; pair every remaining `\trusted`
with a named feature-plan gap."

Why baseline isn't enough for these areas: proxy-claims and `\trusted`
markers accumulate silently. A method labelled `\trusted reviewer:` is
indistinguishable from a method that was never attempted — the audit
can't tell whether the trust is intentional or a placeholder.
Cumulative `\trusted` debt is what lets the toolchain claim
"verified" while resting on Tier-2 surface area the size of the
stdlib.

ER's **first step is the source-of-truth squeeze** (see "The source of
truth" above): identify the language's English norm and its reference
implementation, and squeeze the spec between them — *before* any loop
invariant or `\trusted` decision. The habits below are how you then
discharge that squeezed spec; they are worthless on top of a spec that
was never pinned to the source of truth.

The habits that mark ER work (full version lives in
[`csl-from-scratch/SKILL.md` §1.5](../csl-from-scratch/SKILL.md)
and [`csl-from-scratch/references/stdlib-extreme-rigor.md`](../csl-from-scratch/references/stdlib-extreme-rigor.md)):

0. **Squeeze the spec between the two sources of truth** (the first step — above)
1. Loop invariants AND variants on every loop
2. Body verification first; `\trusted` only with a cited blocker
3. Coq/Lean axioms for facts SMT cannot discharge
4. Round-trip axioms for inverse operation pairs
5. Each `\trusted` carries an actionable `cite:_note:` and feature-plan pointer

Case study: a feature phase was declared complete after adding
proof-rocq directives and a new audit step. The
`bin/agent-feature-supervisor` gate passed because it only checked
deny-lists and CI steps, not phase deliverables. When the user asked
**"what was not done?"**, seven gaps surfaced, including the phase's
central claim (promote four `\trusted` methods to body-verified — none
had). ER closes that loop: phases carry `**Acceptance:**` blocks the
supervisor executes; "done" is machine-checked, not self-declared.

The principle: a phase is DONE when its acceptance claims pass — not
when its target files were touched, not when the gate is green, not
when the implementer feels satisfied.

## What family members exist, and what they share

| Tool | Language | Parser | Status |
|---|---|---|---|
| PyCSL | Python | libcst | shipped |
| ccsl | C | libclang | planned |
| gocsl | Go | go/parser | planned |
| jscsl | TypeScript | TS Compiler API | planned |
| rustcsl | Rust | (contribute to Creusot) | planned |
| cppcsl | C++ | LibTooling (layer on TrustInSoft/Frama-Clang) | planned |

All members share:

- The `proof2why3` extraction and cross-check pipeline.
- The shared first-order IR for spec statements.
- The `proof rocq <qualname>` / `proof lean <qualname>`
  directive surface (with language-appropriate syntax — `#@`, `//@`,
  `/*@ @*/`, `#[...]`).
- The Rocq+Lean proof directory convention (`<source>.proofs/{rocq,lean}/`).
- The qualified-name namespacing.
- The Why3 backend.

What differs between members is only the frontend integration and the
language-specific memory model. The IR, the bridge, the cross-check,
and the proof-side conventions are universal.

## How to answer common tactical questions

**"Where should I put this new specification?"**
In Rocq and Lean, as paired theorems under a qualified name. Cite from
the source file with `proof rocq` and `proof lean`. Avoid
hand-written Why3 axioms unless the property is something Why3 stdlib
already provides (in which case use the language's `uses`/`requires`
mechanism for stdlib import).

**"Should I add a feature to the bridge for X?"**
Probably not. The bridge is content-free. If X is source-language
specific, it belongs in the host verifier. If X is a new translation
rule for the IR, it must apply identically to both Rocq and Lean
extractors. Default answer is "the bridge stays small."

**"Can I just use one prover?"**
Yes, with an explicit override. No, by default. Single-prover mode is
an escape hatch for early development or for properties that have not
yet been ported to the second prover. Production code should use
both.

**"What if Rocq and Lean disagree?"**
Halt. Print the structured diff. Do not pick a winner. The user
either fixes one side or accepts the disagreement explicitly via
config. The CI gate is the load-bearing component of the trust
story.

**"Should I build a verifier for language X from scratch?"**
Almost always no. Check first whether a Why3-targeting verifier
already exists for the language. If yes (Creusot for Rust, TrustInSoft
or Frama-Clang for C++), contribute `proof` support to that
verifier rather than building a parallel tool. The contribution is
small, additive, and uses the host verifier's mature machinery for
everything else.

**"What about [non-Why3 verifier]?"**
The architecture targets Why3 specifically because the ecosystem
matters. Viper-based tools (Nagini, Gobra, Prusti) could in principle
implement `proof` against Viper instead, but that's a separate
project and not part of the family.

## What this skill is NOT

This skill teaches philosophy, not tactics. For specifics:

- For parser/frontend choices per language, refer to the per-language
  design documents (e.g., the C frontend choice doc, the Go choice doc).
- For the `proof2why3` pipeline internals, refer to the bridge plan.
- For PyCSL annotation syntax, refer to the PyCSL annotation reference.
- For specific Rocq or Lean proof tactics, this skill says nothing —
  the proofs are normal proofs, written by humans with proof-assistant
  expertise.

The point of this skill is to make sure that tactical answers, when
they come, are anchored in the right philosophy. Most *CSL design
questions have an obvious answer once the philosophy is internalized.
The skill exists because the philosophy is unusual enough to be
non-obvious by default.

## One closing observation

The deliverable of this project is a convention with a reference
implementation, not a collection of verifiers. The verifiers exist
to demonstrate that the convention works. If the convention catches
on, it should be adopted by every deductive verifier that targets
Why3 — and the *CSL-specific tools become first consumers, not the
endpoint.

When making any design decision, ask: does this strengthen the
convention, or does it strengthen the implementation at the
convention's expense? The first is almost always the right answer.

## Proof-strategy hierarchy when SMT struggles (leaf-first, composition-first)

When a goal won't discharge, the order of escalation matters — and the cheapest
move is usually structural, not a bigger hammer:

1. **Leaf-first.** Don't strengthen the contract at the *top* of a call chain —
   go to the LEAF functions and give them correct VALUE contracts (not just
   shape/length). A byte `_pack_uint16_be` must say `\result[0]*256 +
   \result[1] == v`, not merely `\length(\result) == 2`; its inverse `_unpack`
   must reconstruct it (round-trip). Without true leaves the composers above have
   nothing true to build on. Stuck deductive proofs → fix BOTTOM-UP: leaves →
   composers → top. (Each layer, when attempted, also tends to surface the one
   foundational tool gap beneath it — e.g. contract `\result[i]` lowering to an
   opaque `subscript_get` instead of `Array.get` — invisible from the top.)

2. **Compose, don't re-derive.** When a VC times out re-deriving a fact over a
   large state — e.g. the 4-term big-endian byte decomposition over a 64-element
   array in `_pack_inode` — do NOT make SMT redo the arithmetic. CALL the
   already-proven leaf and copy its bytes, so the field property follows from the
   leaf's contract by COMPOSITION. This beat a hard SMT timeout with zero new
   proof obligations (no Rocq, no Lean, no axiom). Composition is the first escape
   from the "SMT-can't" wall — cheaper than any external proof.

3. **Cross-validated lemma (the Rocq+Lean escape).** For a genuinely-SMT-hard
   *reusable fact* (inductive properties, bitwise identities, struct round-trips),
   prove it in Rocq AND Lean (defense-in-depth), register it in `_AXIOM_REGISTRY`,
   cite with `#@ proof rocq/lean`. Citing makes the VC prove FAST in SMT (the
   axiom is a hypothesis the solver just applies) — so the citation solves
   soundness AND the timeout-wait at once. NB there is no Why3→Lean backend:
   "Rocq+Lean" means the LEMMA STATEMENT is independently proven in both, then
   cited as a Why3 axiom (not the raw VC discharged in Lean).

4. **A `#@ no_smt` skip keyword is the wrong lever.** Skipping SMT with no
   replacement is `\trusted` by another name — the goal silently enters the TCB
   (unsound). Paired with a citation it is redundant (a cited axiom isn't
   SMT-proven anyway, and the citing VC proves fast). If the *pain* is dev-loop
   latency, expose a configurable `--timelimit`, not a goal-level skip.

5. **Proof TIME is a constraint, not just provability.** A richer contract that
   proves STANDALONE can still blow the full-module proof past a wall-clock budget
   (round-trip field-ensures that prove in `--fun` can push a whole-module proof
   over its limit). Verifiability and verification-cost are distinct; a faithful
   model must be both provable AND affordable to re-verify — which sometimes
   argues for a modular boundary (`#@ no_inline`: prove the heavy function once,
   reuse its contract in callers instead of re-proving the inlined body).

## The descent and the return: from English spec to formal test

The source-of-truth principle and the leaf-first hierarchy above are the two ends
of one arc, and seeing the whole arc is the point. A *CSL proof is a **descent and
a return** — `docs/formal-filesystem.md` walks it end-to-end with the `os` module
(a Unix inode filesystem, proved with **0 unproven goals** on a one-line trusted
base) as the worked example.

- **The descent.** The external English specification becomes a *faithful* model
  (real semantics, never a convenient abstraction — bytes if the real thing is
  bytes; partiality kept, not totalized), and the model becomes its **smallest
  checkable contracts**: the leaf whose honesty fits in a glance (`_pack_uint16_be`
  *ensures* `\result[0]*256 + \result[1] == v`).
- **The return.** Those leaf contracts are proved, and each higher layer is proved
  *resting on the proved contracts beneath it* (compose, don't re-derive), climbing
  leaf-to-API until — at the apex — you write the specification out **again**, as a
  **formal test** whose postcondition transcribes the English promise and is
  discharged over *symbolic* inputs.

The hinge between descent and return is the distinction worth internalizing:
**a test asks *did it work this time*; a proof asks *could it ever fail*.** A
concrete test fixes the inputs and samples a measure-zero slice of an input space
larger than atoms; a verification condition quantifies over a *symbol* standing for
every input and proves the solver cannot break it. The very scenario you ran
concretely to convince yourself the model is right (the rehearsal) becomes, with
its inputs made symbolic, the thing that proves it right for everyone. That return
— the specification re-stated as a discharged formal test — is what turns *we
believe it* into *it cannot fail*. (Mind the strength you claim: proving a driver
*never faults* on any input — totality/safety — is a weaker, usually-earlier
promise than proving it *returns the right answer* on any input — functional
content. Different theorems; state which one you have.)
