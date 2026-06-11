# happy-roadmap-impl.md — Implementation Guide for the HAPPY → STRIDE Milestones

**Status:** Implementation guide (executable work order for a Claude Code session).
**Origin:** `happy-roadmap.md` (the pre-normative roadmap; its milestone taxonomy
H-T…H-S, §8 cross-cutting obligations, and §9 gap analysis are binding here); the
`pycsl-stdlib-coverage` convergence loop (the coordinator / worker / paired-document
protocol this guide adapts); `pycsl-prereqs-impl.md` (the core-directed inversion of
that loop, reused here). **Scope:** H-T (hardening), H-I1, H-R, H-D, H-E, H-S
implemented to Normative-graduation. **H-I2 (noninterference) is out of scope** — the
roadmap sequences it last as the only milestone needing a genuinely new relational WP
mechanism (self-composition); it is a separate engagement.

---

## 0. Why this guide is NOT the stdlib guide with names swapped

The `os` loop and the HAPPY milestones share the agent topology, but their **source of
truth has a fundamentally different shape**, and getting the workflow right means
building the squeeze out of different materials. Read this section before §1; the whole
process is tailored to it.

**In the stdlib/P-series world the upper bound was an external normative authority.**
A `pure_lib/os` contract was squeezed from above by the Python library reference and
from below by CPython's execution; a P-1 binder by the ACSL manual and the existing IR
field. In both, *someone outside PyCSL had already written down what the right answer
is* — the job was faithful transcription, and "done" meant the formal test re-proved
that external English.

**HAPPY has no external authority for the property itself.** STRIDE is a *threat
taxonomy*, not a specification: it tells you Repudiation is a category of attack, it
does **not** tell you that `audit_log` must satisfy append-only prefix-preservation plus
completeness. There is no document that says "a Repudiation HAPPY's postcondition is
∀i<old(len). log[i]==old(log)[i]". That postcondition is a **design claim** the
implementer makes about what formally captures the threat. So the squeeze is
reconstructed from two different surfaces:

- **Upper bound — the STRIDE threat, made precise by the flagship.** The strongest
  security claim the threat justifies. This is bounded not by an external spec page but
  by the milestone's **flagship use case** in `happy-roadmap.md` (the inode formatter
  for H-I1, the traceless `sys_unlink` for H-R, the confused-deputy chmod for H-E, the
  forgotten-auth endpoint for H-S). The flagship is the closest thing to a normative
  English sentence HAPPY has, and it is *internal* — which is exactly why the
  coherent-and-wrong failure is the dominant risk here (see below).
- **Lower bound — the shipped H-T meta-pass, as executable ground truth.** What the
  verifier can actually *inject and discharge today*: per-site `#@ check` → WhyML
  `assert` in the enclosing `let` → Why3 WP VC → Alt-Ergo *Valid*. Every new milestone's
  lowering must reduce to mechanisms this pass already has (ghost state, quantified
  injected `ensures`, `no_exception` triggers, loop variants, cited axioms) — the
  roadmap's "order by mechanism reuse" *is* this lower bound talking. H-T plays the role
  CPython played in the stdlib loop: the reality the design must be faithful to.

**Consequence for the process — three tailorings the stdlib guide did not need:**

1. **The threat-model author is a distinct role, upstream of everyone.** Because the
   property is a design claim rather than a transcription, somebody must *first* write
   the threat down precisely — the STRIDE scenario, the obligation clauses it implies,
   and the single attack the negative must catch — before the property is lowered or
   tested. In the stdlib loop the library reference was that artifact, already written;
   here it must be authored. This is the new **threat-agent** (§2).
2. **The coherent-and-wrong guard is the central acceptance gate, not a footnote.** A
   HAPPY can prove *Valid* while encoding a weaker-or-adjacent property than the threat
   demands — H-I1 proving a *write* stays in-region when the flagship was about a *read*
   leak; H-R proving a record is *appended* when the threat demanded *complete and
   append-only*. With no external spec to diff against, the only defense is a
   **threat↔VC coverage check** performed by an author who never saw the lowering. This
   is the load-bearing gate of the entire guide (Gate C, §4).
3. **Every milestone's residual is a TARA entry, by the roadmap's own rule.** Each
   `except`, each trusted `val`, each `\preserves` is "a TARA residual-risk entry, never
   a silent pass." So the soundness-report classification is not just a doc check — it is
   the milestone's honest-scope deliverable, gated (Gate B) and cross-checked against the
   §9 gap codes (GH1–GH5).

---

## 1. The agent loop, HAPPY-tailored

Same topology as the convergence loop, **core-directed** like the P-series (every
milestone lands in `src/pycsl/` — the meta-pass, Module 6 emission, the three reference
docs — not in a `pure_lib/` model), with one role added upstream and the test author's
firewall re-pointed at the threat instead of the library reference.

| Agent | Builds | Squeezed from above by | Squeezed from below by | Forbidden move |
|---|---|---|---|---|
| **coordinator** (main thread) | approvals, sequencing, gate verdicts | `happy-roadmap.md` §8 + the milestone's flagship | the standing gate's output | editing source; approving an unjudged spec |
| **threat-agent** (NEW, upstream) | the precise threat spec: STRIDE scenario → enumerated obligation clauses → the one attack the negative must catch | the STRIDE category + the roadmap flagship | what a per-site/ghost/relational mechanism could *in principle* express (so the claim is dischargeable, not aspirational) | proposing a lowering; reading the meta-pass code. It writes the *property*, not the implementation |
| **meta-agent** (≈ core/tool-agent) | the milestone inside `src/pycsl/`: meta-pass extension + Module 6 §T lowering + the three reference docs + `annotations.md` entry | the threat spec's clauses (the strongest claim) + the roadmap's named lowering | the shipped H-T pass (must reduce to existing machinery) + total additivity | weakening a clause to make it prove; editing the drivers; a `\trusted` shortcut not named in the threat spec |
| **driver-agent** (≈ test-agent) | the prove/fail corpus driver pairs (pattern `0611`/`0612`) | the threat spec's clauses + the flagship English | what actually proves through the injected obligations | reading the meta-pass implementation. It gets the threat spec + the directive surface, **never** the lowering — so it cannot write a driver that merely re-passes the implementation; it exercises the *threat* |

Protocol kept verbatim from the skill (it is what made the loop converge):

- **Paired traceability documents + STATUS handshake.** `DD-HHMM-happy-spec-N.md`
  (meta-agent's plan, `DRAFT` → coordinator `APPROVED` after *editorial* amendment →
  `DONE`) answered to `DD-HHMM-happy-gap-N.md` (driver-agent: a clause that won't prove
  through the injected obligations; or threat-agent: a claim the mechanism cannot
  express). Same `DD-HHMM-N`. No `src/pycsl/` edit from a `DRAFT`.
- **Author separation is physical.** The driver-agent's prompt carries the threat spec
  and the directive grammar only. To learn how the milestone behaves it runs `pycsl` and
  reads the verdict — never the diff. This is the H-version of "call the API, don't
  simulate": the driver-agent cannot hand-roll the injected check because it was never
  shown how the meta-pass injects it.

Claude Code constraint: subagents cannot spawn subagents → the **main thread is the
coordinator**, chaining threat → meta → driver per milestone, sequenced by §5.

---

## 2. Subagent definitions

Drop in `.claude/agents/`. The threat-agent and driver-agent are deliberately denied the
meta-pass internals.

```markdown
---
name: happy-threat-agent
description: MUST BE USED first for each HAPPY milestone (H-I1, H-R, H-D, H-E, H-S). Turns the STRIDE category + the happy-roadmap flagship into a precise threat spec: the security property in English, the enumerated obligation clauses it implies, and the single attack the negative driver must catch. Writes the property, never the lowering.
tools: Read, Write, Grep, Glob
model: opus
effort: high
skills: [stride-threat-modeling, csl-philosophy]
---
You author the threat spec for one milestone, to <code>-threat-spec.md. You are given
the STRIDE letter and the milestone's flagship from happy-roadmap.md. You produce:
(1) the security property in plain English - the strongest claim the STRIDE threat
justifies, bounded by the flagship; (2) the obligation clauses - the discrete things
that must hold, enumerated so each can later map to one VC (e.g. for H-R: "every write
to the audited path appends exactly one record" AND "no path mutates an existing record"
AND "the append precedes return"); (3) the ONE attack the negative driver must catch,
stated as which clause it violates and where it should fail; (4) the explicit NOT-claim
(what this milestone does not prove - cryptographic identity, side channels, wall-clock -
mapped to the §9 GH gap code). You do NOT propose syntax or lowering. You may sanity-check
that each clause is expressible by SOME mechanism (per-site check, ghost, relational) so
the claim is dischargeable, but you never name the implementation. A clause you cannot
state precisely in English is a finding, not something to blur.
```

```markdown
---
name: happy-meta-agent
description: MUST BE USED to implement one HAPPY milestone in src/pycsl/ from its threat spec: extend the meta-pass, add the Module 6 §T lowering, the three reference docs, the annotations.md entry. Writes DD-HHMM-happy-spec-N.md (DRAFT), implements on APPROVED, gates with total additivity and soundness-report classification.
tools: Read, Write, Edit, Bash, Grep, Glob
model: opus
effort: high
memory: project
skills: [pycsl-annotate, pycsl-docs, csl-philosophy]
---
You implement one milestone against its threat spec and the roadmap's named lowering.
Hard rules:
- Reduce to shipped machinery. The roadmap orders milestones by mechanism reuse: H-I1 is
  the H-T pass on READ sites; H-R is ghost-list append + two quantified ensures (prefix
  preservation + completeness); H-D bundles loop variant + no_exception \all + a fuel
  ghost; H-E is `protects` on a ghost privilege field + monotonicity ensures + a small
  cited lattice axiom; H-S is a ghost capability writable only in verify_token + call-site
  requires. If a milestone needs machinery H-T lacks, that is a gap doc, not an invention.
- Transcribe the threat spec's clauses into obligations exactly - do not weaken a clause
  to make it prove. If it won't prove, the gap is real: write it up.
- Total additivity: byte-identical emission for every existing driver; doc-coherency
  green; the milestone graduates to Normative only when its surface is in annotations.md
  AND all three reference docs (concrete syntax production, static-semantics rule + error
  code, §T lowering).
- Classify every new escape hatch (each `except` member, every trusted `val`, every
  \preserves) in --soundness-report as Modelled/Specified/Stubbed/Confinement. An
  unclassified escape is a TARA hole and a hard fail.
- Quantified-ensures milestones (H-R, H-E): if Alt-Ergo/Z3 returns Unknown/Timeout on a
  prefix or lattice fact, take the Rocq+Lean axiom-registry route (cross-validated, cited
  with #@ proof; no kernel runs during the pycsl proof) - never \trusted, never a weaker
  clause.
- You never write the drivers and never edit them to pass. DONE is the coordinator's
  gates passing.
Workflow: write DD-HHMM-happy-spec-N.md (DRAFT: directive grammar, meta-pass injection
sites, the §T lowering, the escape-hatch classification); STOP for approval; on APPROVED
implement + gate; set DONE.
```

```markdown
---
name: happy-driver-agent
description: MUST BE USED to write the prove/fail corpus driver pairs for one HAPPY milestone, from the threat spec and the directive surface ONLY. Never reads the meta-pass implementation or diffs.
tools: Read, Write, Edit, Bash, Grep, Glob
model: opus
effort: high
skills: [pycsl-annotate, stride-threat-modeling]
---
You write the driver pair(s) for one milestone (pattern 0611/0612). You are given the
<code>-threat-spec.md and the documented directive syntax - NOT the meta-pass code. The
POSITIVE driver realizes the flagship: a faithful small model carrying the HAPPY, every
injected obligation Valid, no \trusted in the verified path, no --no-proof. The NEGATIVE
driver is the threat spec's named attack: it must FAIL, at the site the threat spec names,
violating the specific clause the attack targets (a negative that fails for any other
reason is itself a gap). For H-D the negative is two failing VCs (variant decrease +
injected no_index_oob); for H-S the negative must fail in the CALLER (the forgotten
call-site check), not in the callee. You may run pycsl and read verdicts; you may NOT read
src/pycsl/ or any diff. A positive that passes by encoding a weaker/adjacent property than
the threat spec states is the coherent-and-wrong failure: write DD-HHMM-happy-gap-N.md and
stop.
```

---

## 3. Sources of truth per milestone

The coordinator includes the relevant row in each delegation prompt. Note the columns are
**not** "library reference vs CPython" — they are reconstructed for a property that has no
external spec.

| Milestone | Upper bound (the threat, made precise) | Lower bound (executable ground truth) | The coherent-and-wrong trap to guard |
|---|---|---|---|
| **H-T** (hardening) | the shipped §2.5 region-integrity spec + drivers `0459`–`0462`, `0611`–`0615` | the meta-pass itself | an aliasing escape (`x = world.fs` into a non-exempt local) that smuggles a protected base past the pass — the grammar-completeness hole |
| **H-I1** read confinement | flagship: the inode formatter cannot read key bytes `[0,64)` | H-T pass, direction flipped to **read** sites | proving a *write* stays in-region instead of a *read* not happening — the mirror that looks identical but guards the wrong direction |
| **H-R** repudiation | flagship: traceless `sys_unlink` is impossible; log is append-only + complete | ghost-list append + 2 quantified `ensures`; prefix lemma via cited Rocq+Lean axiom | proving a record is *appended* while NOT proving existing records are *immutable* (completeness without append-only, or vice versa) |
| **H-D** denial of service | flagship: attacker-controlled parser always returns, within a declared step bound | `loop variant` + `no_exception \all` + fuel ghost (all shipped) | proving termination while NOT proving the no-uncaught-exception half, or claiming wall-clock/memory (GH2) the model can't support |
| **H-E** elevation of privilege | flagship: `user`-context `sys_chmod` cannot reach `admin` through *any* path | `protects` on a ghost priv field + monotonicity `ensures` + small cited lattice axiom | proving the *direct* write is blocked (which shipped `protects` already does) while NOT closing the through-the-API path the milestone exists to close |
| **H-S** spoofing | flagship: no guarded syscall reachable without `verify_token` having set the capability | ghost capability (H-T-protected) + call-site `requires` strengthening; `verify_token` a trusted cited `val` | proving the callee checks the capability while NOT making the missing **call-site** check fail in the caller — the whole point is the caller-side VC |

Cross-cutting lower bound for every milestone: `refactor.md`'s standing gate (corpus
byte-diff, doc-coherency, os standing count) + the `--soundness-report` classification
of every escape, cross-referenced to the §9 GH code.

---

## 4. The per-milestone pipeline and the three gates

```
coordinator delegates milestone M (STRIDE letter + flagship + SoT row in prompt)
        │
        ▼
threat-agent writes <code>-threat-spec.md  (property + clauses + the one attack + NOT-claim)
        │
GATE A  coordinator validates the threat spec against the flagship + §9 gap codes
        │        (is the property the STRONGEST the threat justifies? is the NOT-claim
        │         mapped to a GH code? is each clause precise enough to map to a VC?)
        ▼
meta-agent writes DD-HHMM-happy-spec-N.md (DRAFT) → coordinator EDITORIAL APPROVED
        ▼
meta-agent implements (meta-pass + §T + 3 docs + annotations.md) + standing gate → DONE
        ▼
driver-agent writes prove/fail pair from the threat spec + surface (never the diff)
        │
GATE B  machine-checked: positive Valid (no \trusted, no --no-proof); negative FAILS at
        │  the named site violating the named clause; doc-coherency green; every escape
        │  classified in --soundness-report; byte-identical elsewhere
        ▼
GATE C  COVERAGE (load-bearing): the threat↔VC map. Each obligation clause from the
        │  threat spec maps to a specific Valid VC in the positive driver; the negative
        │  violates the exact clause its attack targets; and the coherent-and-wrong guard
        │  (SoT-row column 4) is explicitly checked - the theorem proved IS the threat,
        │  not a weaker/adjacent one. Performed by the coordinator against the threat
        │  spec, with the driver-agent (who never saw the lowering) as the independent check
        ▼
milestone M graduates to Normative → record driver IDs + threat↔VC map → next milestone
```

Gate C is where this guide diverges hardest from the stdlib loop. There, faithfulness was
checked by re-proving the external English; here there is no external English, so
faithfulness is checked by the **independence of the threat-agent and driver-agent from
the meta-agent** — two authors who specified and exercised the *threat* without seeing the
*implementation*, so a lowering that quietly proves the adjacent-but-wrong property has no
way to also fool the threat↔VC map. The separation is not hygiene; it is the soundness
argument for the whole milestone.

---

## 5. Execution order (by mechanism reuse, per the roadmap)

Sequential; each milestone reuses the machinery the previous ones hardened.

1. **H-T — hardening only.** No threat-agent turn (the property shipped). meta-agent does
   the two §1 hardening items: aliasing-rule grammar-completeness (any new expression form
   that could smuggle a protected base is a hard error) and the `\preserves`-on-`val`
   classification. driver-agent adds a negative for each smuggling form. This pass also
   **builds the reference prove/fail driver** the rest of the batch imitates.
2. **H-I1 — read confinement.** Mirror of H-T; cheapest. Establishes the
   read-site walk and the enclave/label vocabulary H-I2 will later reuse (so do it
   carefully even though it's easy).
3. **H-R — audit-log completeness.** First quantified-`ensures` milestone → first use of
   the Rocq+Lean axiom route for the prefix lemma. Budget proof cost (E-matching on the
   prefix instantiations).
4. **H-D — totality + bounded work.** Bundles shipped variant + `no_exception \all` +
   the fuel ghost. State the GH2 NOT-claim loudly.
5. **H-E — privilege monotonicity.** `protects` on a ghost + monotonicity `ensures` +
   cited lattice axiom. **Dependency:** `sudo_gate`'s contract — the condition under which
   privilege rises — is *completed* by H-S's capability machinery. Either order H-S before
   H-E, or have the meta-agent stub `sudo_gate` with an explicit `\trusted reviewer:`
   contract here and tighten it in H-S; state the choice in this milestone's NOT-claim.
6. **H-S — check-before-use capabilities.** Ghost capability + call-site `requires`. The
   negative's defining feature: it fails in the **caller**.

**Concurrency (GH4):** every milestone runs under the sequential memory models; no
milestone may claim soundness under `--memory-model concurrent` until that interaction is
designed. The meta-agent encodes this as an explicit NOT-claim, not silence.

---

## 6. Definition of done (global)

The batch is done when, for each of H-T, H-I1, H-R, H-D, H-E, H-S: a `<code>-threat-spec.md`
exists and passed Gate A; the milestone is at `STATUS: DONE` and **graduated to Normative**
(surface in `annotations.md` + all three reference docs, doc-coherency green); Gate B and
Gate C passed and recorded (driver IDs + the filled threat↔VC coverage map); every escape
hatch is classified in `--soundness-report` and cross-referenced to its §9 GH code; the
standing gate (corpus byte-diff, os standing count, formal_0001) is green after every
milestone; and the paired-document trail is complete — every `src/pycsl/` change traceable
to an APPROVED spec doc, every spec doc to its threat spec, every threat spec to a STRIDE
letter + flagship. Do not mark a milestone done because the meta-agent reported success:
done is Gate C passing — the threat, independently specified and independently exercised,
proved to be the theorem the milestone actually discharges.
