# typing-global-impl.md — Implementation Guide for the Python `typing` Module

**Status:** Implementation guide (executable work order for a Claude Code session).
**Origin:** `typing-global-overview.md` (the pre-normative strategy; its S1–S7 sources of
truth, the two-plane squeeze, the TY0–TY3 tiers, the GT1–GT8 gaps, and the
Interpreted/Shimmed/Ignored soundness classification are binding here); the
`pycsl-stdlib-coverage` convergence loop (the coordinator / worker / paired-document
protocol this guide adapts); `pycsl-prereqs-impl.md` and `happy-roadmap-impl.md` (the
core-directed inversion and the upstream-spec-author tailoring, both reused here).
**Precondition:** this engagement runs **after** the P-series (a settled IR/emission
platform) and HAPPY (a hardened meta-pass and the `--soundness-report` machinery), with
the PEP 695 `pure_ast` parser productions landed before TY3 — per the overview's
sequencing. **Scope:** TY0, TY1, TY2, and TY3 to Normative-graduation. The permanent-
refusal gaps (GT1 `Any`, GT6 `# type: ignore`, GT7 the `Protocol` runtime/static split)
are *specified*, not *solved*, at their owning tier (§5).

---

## 0. Why this guide is different again: two planes, two squeezes

The three prior efforts each had a single squeeze, even when its materials differed:
`os`/P-series squeezed a contract between an external authority (library reference, ACSL
manual) and an execution ground truth (CPython, the IR field); HAPPY squeezed a property
between a STRIDE threat and the shipped meta-pass. `typing` is the first effort whose
meaning **splits across two planes that have independent squeezes and must never be
blended**. Getting the workflow right is getting that non-blending enforced by
construction.

- **The static plane.** What a typing construct *means as a judgment about programs*:
  assignability, narrowing, `Protocol` conformance, overload resolution, generics.
  - *Upper bound:* **S1**, the typing specification (typing.readthedocs.io, under the
    Typing Council) — the strongest static judgment the spec justifies; **S1 supersedes
    the defining PEPs (S2) where they conflict**.
  - *Lower bound:* what PyCSL's IR and WhyML emission can *soundly* express — and unlike
    every prior effort, this bound is allowed to be **stricter** than the upper bound,
    never weaker. Where the type system is deliberately unsound (`Any`'s consistency
    relation, `# type: ignore`), PyCSL refuses to import the unsoundness. Divergence-by-
    strictness is legitimate and recorded; divergence-by-weakness is a bug.
  - *Executable ground truth:* **S5**, the typing conformance test suite — the static
    plane's analogue of CPython execution. PyCSL declares the subset it conforms to and
    runs it as a gate.

- **The runtime plane.** What a construct *does when the program runs* — which for most
  of `typing` is almost nothing.
  - *Upper bound:* **S3**, the library reference, whose central sentence is **negative**:
    the runtime does not enforce annotations. A shim that *checks* anything S3 says is
    unchecked is unfaithful in exactly the way an over-strong axiom is. `cast(t, v)`
    carries `ensures \result == v`, full stop.
  - *Lower bound:* **S4**, the observable behaviour of CPython's `Lib/typing.py`
    (identity functions, introspectable objects, `TypedDict` being a plain `dict`).

- **The seventh source, and why TY0 comes first. S7** is *PyCSL's own current front-end
  behaviour*. The bootstrap fact: every `def sys_write(self, fd: int, buf: bytes) -> int`
  in `pure_lib/os` is already the front-end interpreting a fragment of `typing` into IR
  and WhyML types. That de facto implicit subset must be **transcribed into the
  references (TY0) before a single construct is added** — otherwise the effort grows
  features on top of an unspecified interpreter inside a verifier whose identity is "no
  unspecified behaviour."

**The no-blending rule is the source of the dominant failure mode, and therefore the
shape of the process.** A construct whose two planes disagree carries **both** contracts,
separately labelled, never merged. The canonical trap: a `@runtime_checkable Protocol`'s
`isinstance` checks method *presence only* (S3/S4), while static conformance is full-
signature behavioural refinement (S1). Letting the weak runtime check stand in for static
conformance — or encoding the static meaning into the runtime check — is the coherent-
and-wrong failure, typing edition. Three tailorings follow:

1. **An upstream author whose deliverable is the *two-plane spec*, not one claim.** Per
   construct: the static claim (cite S1/S2), the runtime claim (cite S3, resolved by S4),
   and an *explicit divergence statement* with the Interpreted/Shimmed/Ignored
   classification. This is the **spec-agent** (§2), the typing analogue of HAPPY's
   threat-agent — but its defining discipline is keeping the planes apart.
2. **Two executable ground truths, carried by one independent author.** The static plane
   is gated by an S5 conformance subset; the runtime plane is gated by S4 shim-
   faithfulness drivers. Both are written by a **conformance-agent** who never sees the
   lowering — so neither gate can be tuned to the implementation.
3. **Gate C is half machine-checked, half independence-based.** Typing sits *between* the
   stdlib loop (fully external ground truth) and HAPPY (none): its static plane has S5 as
   real external ground truth and its runtime plane has S4, but the *combination rule* —
   no blending — has **no external authority** and is defended only by the independence
   of the spec-agent and conformance-agent from the core-agent. Name this explicitly; it
   is the soundness argument for the whole construct.

---

## 1. The agent loop, typing-tailored

Core-directed (every construct lands in `src/pycsl/` — the front-end normalization pass,
the Module 6 lowering table, the monomorphizer — plus the thin `pure_lib/typing` shim and
the three reference docs). Four workers under the coordinator: one more than the prior
efforts, justified because typing has two distinct executable ground truths (S5, S4) plus
a transcription prerequisite (S7/TY0) plus a feasibility risk (monomorphization).

| Agent | Builds | Squeezed from above by | Squeezed from below by | Forbidden move |
|---|---|---|---|---|
| **coordinator** (main thread) | approvals, sequencing, gate verdicts | the overview's tier plan + S1 precedence | the standing gate + the S5-subset result | editing source; approving an unjudged spec; letting a construct ship with the planes merged |
| **spec-agent** (upstream) | the per-construct **two-plane spec**: static claim (S1/S2), runtime claim (S3↓S4), explicit divergence, Interpreted/Shimmed/Ignored classification | S1 (superseding S2) | expressibility — each claim must be dischargeable by *some* mechanism, so it is a spec not a wish | proposing lowering; **blending the planes** into one contract; reading `src/pycsl/` |
| **core-agent** | the construct in `src/pycsl/` + the shim + the three docs | the two-plane spec's claims | sound expressibility (**may be stricter than S1**, never weaker) + shipped machinery + total additivity | weakening a claim to prove; importing an unsoundness (`Any`, `type: ignore`) to "support" it; editing the conformance suite or drivers |
| **conformance-agent** (executable ground truth) | the declared **S5 conformance subset** (static gate) + the **S4 shim-faithfulness drivers** (runtime gate) | the two-plane spec + S5/S4 | what actually passes | reading the lowering. It gets the two-plane spec + the construct surface, **never** `src/pycsl/` internals — so a conformance pass cannot be reverse-engineered from the implementation |
| **probe-agent** | TY0 witness drivers (pin S7); the TY3 **monomorphization feasibility probe** (prove one instantiation before the collection/emission machinery); the cost probes (per-instantiation VC volume; relational/doubled-state E-matching) | the design claim under test | the front-end's and Why3's **actual** behaviour | implementing a fix; a probe writes a verdict, never a feature |

Protocol kept verbatim (it is what made the loop converge): paired
`DD-HHMM-typing-spec-N.md` (core-agent plan: `DRAFT` → coordinator `APPROVED` after
*editorial* amendment → `DONE`) answered to `DD-HHMM-typing-gap-N.md` (conformance-agent:
a construct that fails its S5 subset or whose shim diverges from S4; spec-agent: a claim
no mechanism can express; probe-agent: a verdict contradicting the design). Same
`DD-HHMM-N`; no `src/pycsl/` edit from a `DRAFT`. **Author separation is physical** — the
conformance-agent learns a construct's behaviour by running `pycsl`/the suite and reading
verdicts, never the diff. Claude Code: subagents cannot spawn subagents → the **main
thread is the coordinator**, chaining spec → core → conformance (with probe runs where a
tier needs them), sequenced by §5.

---

## 2. Subagent definitions

Drop in `.claude/agents/`. The spec-agent and conformance-agent are denied the lowering
internals on purpose.

```markdown
---
name: typing-spec-agent
description: MUST BE USED first for each typing construct. Authors the two-plane spec: the static-plane claim (cite S1/S2), the runtime-plane claim (cite S3, resolved by S4), the explicit divergence between them, and the Interpreted/Shimmed/Ignored classification. Writes the property across both planes, never the lowering, and never merges the planes.
tools: Read, Write, Grep, Glob
model: opus
effort: high
skills: [csl-philosophy, pycsl-docs]
---
You author <construct>-twoplane-spec.md for one typing construct. Produce, in separate
sections that must not be merged:
(1) STATIC PLANE - the strongest static judgment S1 justifies (cite the spec section; if
a PEP S2 conflicts, S1 wins and you say so). State narrowing/assignability/conformance/
overload behaviour as obligation clauses, each precise enough to map to one VC or one S5
conformance case.
(2) RUNTIME PLANE - what S3 says happens at runtime, resolved by S4 where S3 is silent.
Remember S3's central sentence is NEGATIVE (annotations are not enforced); a runtime
claim that checks something is almost always WRONG. cast/NewType are identities.
(3) DIVERGENCE - where the two planes disagree (e.g. runtime_checkable Protocol presence
vs static conformance), stated as a permanent two-plane split; neither plane's claim may
stand in for the other.
(4) CLASSIFICATION - Interpreted (static plane lowers it to obligations) / Shimmed
(runtime meaning only) / Ignored (outside the declared subset; tag the GT gap code).
You do NOT propose syntax or lowering. You may check each claim is expressible by SOME
mechanism so it is dischargeable. A claim you cannot state without blending the planes is
a finding, not something to merge.
```

```markdown
---
name: typing-core-agent
description: MUST BE USED to implement one typing construct in src/pycsl/ from its two-plane spec: the front-end normalization, the Module 6 lowering, the pure_lib/typing shim, the three reference docs, the annotations.md entry, the soundness-report classification. Writes DD-HHMM-typing-spec-N.md (DRAFT), implements on APPROVED, gates with total additivity.
tools: Read, Write, Edit, Bash, Grep, Glob
model: opus
effort: high
memory: project
skills: [pycsl-annotate, pycsl-docs, csl-philosophy]
---
You implement one construct against its two-plane spec and the overview's named lowering.
Hard rules:
- Implement BOTH planes separately. The static plane lowers to obligations (Literal ->
  ground requires; Optional/Union -> Why3 sum type with is-None branches as match path
  conditions; Final/ClassVar -> a no-write-outside-__init__ degenerate HAPPY; NoReturn ->
  \diverges/false post; TypedDict/NamedTuple -> WhyML records; overload -> a guarded
  contract family proved against the single implementation; Protocol -> a contract
  interface, conformance as per-method behavioural refinement). The runtime plane is the
  thin shim (cast identity, reified TypeExpr for introspection). NEVER let one plane's
  contract stand in for the other.
- Sound expressibility may be STRICTER than S1, never weaker. Refuse to import unsoundness:
  Any is an opaque type supporting no operation without explicit narrowing (GT1); never
  honour type: ignore (GT6). If a claim won't lower soundly, that is a gap doc - never a
  \trusted shortcut, never a weakened clause.
- TY3 generics: whole-module monomorphization. Collect concrete instantiations; emit one
  name-mangled specialized let/val per instantiation with substituted contracts; a TypeVar
  bound becomes an instantiation-time obligation. Polymorphic recursion is a LOUD-FAIL
  (GT4), never an approximation. Keep per-instantiation VC volume affordable with the same
  no_inline / contract-opacity boundaries used elsewhere.
- Total additivity: byte-identical emission for every existing driver; the os proof and
  formal_0001 re-confirmed; doc-coherency green. A construct graduates to Normative only
  when its surface is in annotations.md AND all three reference docs.
- Classify every construct in --soundness-report (Interpreted/Shimmed/Ignored) and every
  shim escape (Modelled/Specified/Stubbed/Confinement). An unclassified annotation is a
  hard fail.
- You never write the conformance subset or the shim-faithfulness drivers, and never edit
  them to pass. DONE is the coordinator's gates passing.
Workflow: DD-HHMM-typing-spec-N.md (DRAFT: normalization rule, lowering table entry, shim
contract, classification); STOP for approval; on APPROVED implement + gate; set DONE.
```

```markdown
---
name: typing-conformance-agent
description: MUST BE USED to build the executable ground-truth gates for one typing construct, from the two-plane spec and the construct surface ONLY. Curates the declared S5 conformance-suite subset (static gate) and writes the S4 shim-faithfulness drivers (runtime gate). Never reads src/pycsl/ or diffs.
tools: Read, Write, Edit, Bash, Grep, Glob
model: opus
effort: high
skills: [pycsl-annotate, csl-philosophy]
---
You build both gates for one construct from <construct>-twoplane-spec.md and the
documented surface - NOT the lowering.
STATIC gate: select/curate the cases from the typing conformance suite (S5) that the
two-plane spec's static claim commits to; record them as the declared subset; the
construct must conform on every case in its subset. A static claim with no corresponding
S5 case is under-specified - gap doc.
RUNTIME gate: write the shim-faithfulness drivers - cast/NewType identity, introspection
reification - and confirm they agree with CPython Lib/typing.py (S4) behaviour. A shim that
CHECKS something S3 says is unenforced FAILS this gate.
NO-BLEND check (you flag, coordinator rules): confirm the runtime gate does not accidentally
pass the static claim (e.g. a runtime_checkable presence check passing where full
conformance was required). If the only thing proving the static claim is the runtime check,
that is the coherent-and-wrong failure - gap doc.
You may run pycsl and the suite and read verdicts; you may NOT read src/pycsl/ or any diff.
```

```markdown
---
name: typing-probe-agent
description: MUST BE USED to pin reality before implementation: TY0 witness drivers (S7 - what the front-end interprets today), the TY3 monomorphization feasibility probe (one instantiation proven before the collection machinery), and cost probes (per-instantiation VC volume; relational/doubled-state E-matching). Records verdicts; never implements.
tools: Read, Write, Edit, Bash, Grep, Glob
model: opus
skills: [pycsl-annotate]
---
You answer ONE probe at a time with a minimal experiment and a recorded PASS/FAIL verdict.
TY0 probes: one witness driver per annotation form the front-end touches today (scalars,
known class names, container shapes, None returns, stringized annotations), recording the
observed disposition (interpreted / ignored / rejected) - this pins S7 for transcription.
TY3 feasibility probe: prove that a SINGLE monomorphized instantiation (e.g. Stack[int])
discharges end-to-end before any collection/emission machinery is built (the "prove the
rebind first" discipline). Cost probes: measure per-instantiation VC volume and, for any
relational construct, the doubled-state E-matching cost, so the affordability boundary is
evidence not assertion. You write verdicts, never fixes; a surprising verdict is a gap doc.
```

---

## 3. Sources of truth per activity

The coordinator includes the relevant rows in each delegation prompt. The S1–S7 table and
its precedence rule govern *which authority each plane answers to*; the per-tier table
gives the two squeezes and the no-blend trap.

### 3.1 The seven sources and the precedence rule

| # | Authority | Plane it governs | Precedence |
|---|---|---|---|
| **S1** | the typing specification (typing.readthedocs.io, Typing Council) | static — the upper bound | **supersedes S2 on any conflict** |
| **S2** | the defining PEPs (483/484/526/544/586/589/591/593/604/612/646/673/695/742) | static — rationale + fine print | yields to S1 |
| **S3** | the library reference (`typing.html`) | **runtime surface only**; its key sentence is negative | governs nothing static |
| **S4** | CPython `Lib/typing.py` observable behaviour | runtime — the lower bound | the shim must agree |
| **S5** | the typing conformance test suite | static — **executable ground truth** | the declared-subset gate |
| **S6** | the CPython 3.12 grammar / ASDL schema | concrete syntax of annotations + PEP 695 | the `pure_ast` productions |
| **S7** | PyCSL's own current front-end behaviour | the de facto implicit subset | **transcribed first (TY0)** before anything is added |

### 3.2 The two squeezes per tier

| Tier / construct | Static upper (S1/S2) | Static lower (sound, may be stricter) | Runtime upper (S3) | Runtime lower (S4) | No-blend trap |
|---|---|---|---|---|---|
| **TY0** baseline | none new — TY0 *is* the transcription of **S7** into the three references (+ GT5 forward-ref resolution order) | the code's actual behaviour | n/a (annotations already unenforced) | n/a | claiming TY0 interprets more than S7 actually does — pin every form with a witness driver |
| **TY1** Optional/Union/Literal/Final/cast/NoReturn | S1 narrowing + literal/union semantics | sum types + ground `requires`; Final as degenerate HAPPY | cast/NewType are identities (S3) | `Lib/typing.py` identity behaviour | a `cast` that validates; a `Final` enforced at runtime rather than statically |
| **TY2** TypedDict/NamedTuple/overload/Protocol | S1 structural typing + overload resolution + conformance | records; guarded contract family; conformance as behavioural refinement | TypedDict is a plain dict; overload bodies discarded (S3) | dict/tuple runtime shape | **runtime_checkable Protocol presence check standing in for static full-signature conformance** (the canonical GT7 blend) |
| **TY3** TypeVar/Generic/PEP 695/Callable | S1 generics + bound + variance | whole-module monomorphization; bound as instantiation obligation; variance deferred (GT2) | generic aliases are runtime objects | `GenericAlias` behaviour | an un-instantiated generic claiming a per-instance theorem it never emitted |

Cross-cutting lower bound for every tier: `refactor.md`'s standing gate (corpus byte-diff,
os standing count, formal_0001, doc-coherency) + the construct's `--soundness-report`
classification cross-referenced to its GT code.

---

## 4. The per-construct pipeline and the three gates

```
coordinator delegates construct K (tier + the S1-S7 rows + the no-blend trap in prompt)
        │
        ├─ probe-agent runs K's probes (TY0 witnesses; TY3 feasibility/cost) where the tier needs them
        ▼
spec-agent writes <K>-twoplane-spec.md  (static claim | runtime claim | divergence | classification)
        │
GATE A  coordinator validates the two-plane spec: both planes stated SEPARATELY; the
        │        divergence explicit; the classification assigned; S1 precedence honoured;
        │        each static clause mapped to an S5 case it will be gated by. Planes merged → reject.
        ▼
core-agent writes DD-HHMM-typing-spec-N.md (DRAFT) → coordinator EDITORIAL APPROVED
        ▼
core-agent implements both planes + standing gate                         → DONE (claimed)
        ▼
conformance-agent builds the S5 subset (static) + S4 shim drivers (runtime) from the spec + surface
        │
GATE B  machine-checked: total additivity (byte-identical elsewhere, os + formal_0001
        │  re-confirmed); doc-coherency green; the construct classified in --soundness-report
        ▼
GATE C  TWO-PLANE COVERAGE (load-bearing):
        │  (a) STATIC, machine-checked — the construct passes every case in its declared S5
        │      subset; each static obligation clause maps to a passing case / Valid VC.
        │  (b) RUNTIME, machine-checked — the shim agrees with S4; nothing it does enforces
        │      what S3 says is unenforced.
        │  (c) NO-BLEND, independence-based — the runtime gate does NOT pass the static claim
        │      and vice versa; the divergence the spec named is preserved in the implementation.
        │      Defended by the spec-agent and conformance-agent never having seen the lowering.
        ▼
construct K graduates to Normative → record S5 subset + classification → next construct
```

Gate C is the tailoring that makes typing neither the stdlib loop nor HAPPY. Its (a) and
(b) halves are **machine-checked against external ground truth** (S5, S4) — stronger than
HAPPY, which had none. Its (c) half — the rule that the planes do not blend — has **no
external authority** and is defended exactly as HAPPY's coherent-and-wrong guard was: by
the independence of the upstream author (spec-agent) and the ground-truth author
(conformance-agent) from the implementer (core-agent). A lowering that quietly lets the
weak runtime check satisfy the static claim has no way to also fool a conformance subset
authored from the static spec by someone who never saw that lowering.

---

## 5. Execution order and the gap dispositions

Sequential by mechanism reuse, per the overview. **TY0 first (it pins S7 for everything);
the PEP 695 `pure_ast` productions land before TY3.**

1. **TY0 — specify the implicit subset (S7).** probe-agent pins each annotation form;
   core-agent transcribes the verdicts (+ GT5 forward-reference resolution order) into the
   three references, `# cite:`-anchored to S7 file:line. No behaviour change → the standing
   gate passes trivially, which is the check. conformance-agent's gate here is
   *prediction*: from the written spec alone it predicts each witness driver's disposition;
   a wrong prediction means the transcription is ambiguous — gap doc.
2. **TY1 — monomorphic refinements.** Optional/Union/Literal/Final/cast/NoReturn. Cheapest
   lowering, immediate VC value, no type variables. Establishes the sum-type narrowing
   vocabulary (and the `TypeIs`/`TypeGuard` constructor-fact correspondence) that later
   tiers reuse.
3. **TY2 — aggregates and interfaces.** TypedDict/NamedTuple/overload/Protocol. The
   `Protocol`-as-contract-interface work is where the GT7 no-blend trap is sharpest —
   give Gate C (c) extra weight here.
4. **TY3 — the generic layer.** Requires the PEP 695 productions landed and the
   monomorphization feasibility probe **green before any collection/emission machinery**.
   Variance is the deferred second delivery (GT2); polymorphic recursion is a loud-fail
   (GT4).

**Gap dispositions (these are NOT a separate workstream — each is closed at its owning
tier).**

- *Permanent refusals, specified not solved:* **GT1** `Any` (opaque, no operation without
  narrowing) and **GT6** `# type: ignore` (never honoured) are authored as static-semantics
  rules + error codes at TY1; **GT7** the runtime/static `Protocol` split is the divergence
  section of TY2's two-plane spec.
- *Loud-fails (one error code + one fail-corpus driver):* **GT3** `ParamSpec`/`TypeVarTuple`
  (schema-only) and **GT4** polymorphic recursion, both at TY3.
- *Deliverables at their tier:* **GT5** forward-reference resolution order is part of TY0;
  **GT2** variance is TY3's deferred delivery; **GT8** the declared S5 conformance subset is
  the conformance-agent's standing artifact, meaningful only once TY1–TY2 give something to
  conform to.

Carry a one-row-per-GT ledger (tier, disposition, acceptance line) as the honest-scope
artifact — the same instinct as HAPPY's §9 gap analysis.

---

## 6. Definition of done (global)

The engagement is done when, for every construct in TY0–TY3: a `<K>-twoplane-spec.md`
exists with both planes stated separately and passed Gate A; the construct is at
`STATUS: DONE` and **graduated to Normative** (surface in `annotations.md` + all three
reference docs, doc-coherency green); Gate B and Gate C passed and recorded — including the
construct passing its **declared S5 conformance subset** (static), its shim agreeing with
**S4** (runtime), and the **no-blend** check holding; every construct is classified
Interpreted/Shimmed/Ignored in `--soundness-report` and every GT gap is dispositioned in
the ledger; the standing gate (corpus byte-diff, os standing count, formal_0001) is green
after every construct; and the paired-document trail is complete — every `src/pycsl/`
change traceable to an APPROVED spec doc, every spec doc to its two-plane spec, every
two-plane spec to its S1–S7 authorities with S1 precedence honoured. Do not mark a
construct done because the core-agent reported success: done is Gate C passing — the static
plane verified against the conformance suite, the runtime plane against CPython, and the
two proved, by independent authorship, not to have been blended.
