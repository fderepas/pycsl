---
name: sl-auditor
description: >-
  Audits an existing Squeeze Loop (SL) for soundness — checking whether a target
  loop is truly compliant (pairwise-disjoint authority pairs, physically barriered
  contexts, gate-defined "done", a genuine executable lower bound, and demonstrated
  catching of coherent-and-wrong) or is quietly collapsing into a rubber stamp. It
  applies the squeeze's own discipline to the loop under audit: it maps the actual
  (upper, lower) authority pairs and hunts for an actor certifying its own work;
  probes whether each context barrier is physical or merely honorary; confirms an
  executable oracle disjoint from the actor it judges; checks Gate A / Gate B /
  Gate C are present and load-bearing; seeds coherent-and-wrong artifacts to
  calibrate the monitors (flag rate not zero, not saturated); audits the loop's
  accumulated learned skills VIA the sl-monitoring-sl pattern; checks each known
  collapse mode is blocked by a stabilizer; and routes whatever an internal audit
  cannot self-certify to a disjoint base (external / cross-provider / human reviewer).
  Emits a per-dimension findings report with severities. Use when asked to "audit a
  squeeze loop", "review an existing SL", "is this squeeze loop sound", "check my SL
  for collapse", "does this loop actually have disjoint authorities", "is the barrier
  real or honorary", "who certifies the certifier", "is done gate-defined or self-
  reported", "is this monitor a rubber stamp", or "is my loop quietly collapsing".
---

# sl-auditor — auditing an existing Squeeze Loop

This skill is an **audit methodology** for a *target* Squeeze Loop (SL). It does
not design or operate a loop; it interrogates one that already runs and decides
whether it is *actually* sound or only looks sound. The method is the squeeze
turned on itself: every claim the target loop makes about its own soundness is
held between an **upper bound** (the compliance conditions C1–C4 and the
stabilizer set the loop is supposed to satisfy) and a **lower bound** (what the
loop's contexts, oracles, and gates *actually contain and run* when you inspect
them). A loop is "in-band" only as a reading of its design intent that its
inspected reality does not refute.

It depends on a sibling skill. **The soft-output / learned-skill dimension of an
audit IS the `sl-monitoring-sl` pattern** — see *Dimension 6*. This skill does
not re-derive that machinery; it invokes it. For conceptual background on a single
squeeze (the actor-between-two-bounds picture), the `sl-internal` skill may be
consulted if present.

## The one-paragraph model being audited

A squeeze loop holds every actor between an **upper bound** `U` (a citable,
normative *soft* truth — the strongest claim the actor may make) and a **lower
bound** `L` (an executable *hard* truth — a runnable oracle whose verdict the
actor cannot alter). A deliverable is in-band only if it is a reading of `U` that
`L` does not refute; **coherent-and-wrong** is precisely a deliverable that `L`'s
*proxy* accepts while it violates `U`'s intent. The load-bearing rule is
**disjointness**: every actor answers to a *different* `(U, L)` pair, so no single
actor's evidence base suffices to certify the deliverable and each actor's
characteristic blind spot is caught by an actor that cannot share it. An audit
checks that this structure is real and not honorary.

## The compliance contract the audit checks against (the upper bound)

The target loop is **squeeze-loop compliant** iff:

- **(C1) Disjointness.** The authority pairs are pairwise distinct, chosen so the
  intersection of the in-band sets is the correct deliverable while *no single
  pair suffices to certify it*.
- **(C2) Catchability.** For every actor and every characteristic failure that
  survives its own squeeze, some *other* actor's pair makes that failure
  detectable.
- **(C3) Physical barriers.** At delegation time each actor's context contains
  exactly its authorities and the interfaces it must exercise; denied evidence
  (above all, **the implementation, for the actors who judge it**) is *absent from
  the context, not merely off-limits by instruction*.
- **(C4) Gate-defined done.** An item is *done* iff a fixed set of machine-checked
  gates passes; **no actor's self-report contributes to the definition.**

The audit produces a verdict per condition, plus the residual that no internal
check can settle (Dimension 8).

## How to read the rest of this skill

Dimensions 1–7 are the audit checklist. Each is the squeeze's own discipline
pointed at the target. Dimension 8 is the irreducible limit (the disjoint base).
Dimension 9 is the output form. Run them in order: a loop that fails Dimension 1
(no real disjointness) cannot be rescued by passing the later ones.

---

## Dimension 1 — Disjointness audit (C1)

**Question:** are the `(upper, lower)` authority pairs *pairwise distinct*, and
does any actor answer to a bound it can itself relieve or edit?

**Procedure.**

1. **Map the real pairs.** For every actor in the target loop, write down its
   actual `(U_i, L_i)` — the authority that squeezes it from above and the
   executable that squeezes it from below — *as enforced*, not as documented.
   Distrust the org chart; read the delegation prompts and tool permissions.
2. **Pairwise-distinctness check.** Compare pairs. Two actors holding the *same*
   `(U, L)` is the **shared-evidence** collapse: an error in that base propagates
   unchecked because no actor reads from a different one. Flag any duplicate pair.
3. **Self-certification hunt — the central probe.** For each actor, ask: *can this
   actor edit, author, soften, or relieve the very bound that is supposed to catch
   it?* Concretely:
   - Does the implementer edit or author its own acceptance tests / oracle?
   - Does the actor that judges a deliverable also produce it?
   - Can an actor weaken the obligation clause it is later checked against?

   Any "yes" is **self-judging** — the same blind spot, doubled — and is a
   high-severity finding regardless of how the loop is otherwise structured.
4. **Sufficiency check (the subtle half of C1).** Even with distinct pairs, C1
   demands that *no single pair suffices* to certify the deliverable. If one
   actor's evidence base alone is enough to bless the output, the rest of the cast
   is decorative. Confirm the *intersection* is what's correct, not any one pair.

**Pass** = pairs pairwise distinct, no actor relieves its own bound, certification
requires the intersection. **Fail** = any duplicate pair, any self-certifying
actor, or any single-pair-suffices path.

---

## Dimension 2 — Barrier audit (C3)

**Question:** are the context barriers **physical** (the implementation / evidence
is genuinely *absent* from the relevant actor's context) or merely **honorary**
(an instruction not to look)?

**The key probe — read the delegation prompt, not the policy doc:**

- **Can the exerciser / verifier see the implementation?** If the diff, the source,
  or the internals are present in the judging actor's context, the barrier is
  honorary even if the prompt says "do not rely on the code." *An agent that has
  the internals in context will eventually use them.*
- **Can the judge see the thing it judges, from a disjoint source?** The verifier's
  authority must be the *raw ground truth* (the source re-opened at its anchor, the
  artifact re-run) — never the producer's account of it (the writer's notes, the
  records' interpretation fields). If the judge reads the producer's interpretation,
  the barrier between author and judge is honorary.
- **Anchoring tell.** When the exerciser's negatives or the drivers *mirror the
  implementation's quirks*, the barrier has already leaked: the exerciser anchored
  to the implementation rather than to `U`. This is the **honorary-barrier** collapse
  and is directly measurable by the barrier ablation (Dimension 5 / Dimension 7).

**Pass** = denied evidence is structurally absent from each judging context.
**Fail** = "off-limits by instruction" anywhere a barrier is load-bearing, or any
sign of implementation-anchoring in the exerciser/verifier.

---

## Dimension 3 — Lower-bound audit (the executable oracle)

**Question:** is there a genuine **executable** oracle `L` whose verdict the actor
*cannot alter*, and is it *disjoint from the actor* (not the actor's own check)?

**Procedure.**

1. **Existence.** Identify, for each actor, the runnable `L`: a pure function, a
   committed verdict cache, a conformance suite, a re-run of an artifact, a
   type/proof checker. If there is **no executable lower bound**, the loop *cannot
   catch coherent-and-wrong by construction* — coherent-and-wrong is exactly the
   class only `L` rules out. Record this as a structural defect, not a gap.
2. **Immutability.** Confirm the actor cannot edit `L` or its inputs to make itself
   pass (tie back to the self-certification hunt in Dimension 1). An oracle the
   actor can tune is not a lower bound.
3. **Disjointness of `L`.** The oracle must be authored/held by someone *other*
   than the actor it bounds. The implementer's own unit tests are not a lower bound
   for the implementer; they share its blind spot.
4. **Honesty of availability.** If a sub-loop's `L` is not actually runnable in the
   audit environment, say so — `DEPENDENCY UNMET` — and do **not** record a pass for
   that sub-loop. Never fake a green for an unaudited oracle. (This mirrors the
   `sl-monitoring-sl` oracle-availability discipline.)

**Pass** = every actor has a disjoint, immutable, runnable `L`. **Fail** = a
missing `L` (structural — the loop is soft-only), a self-owned `L`, or an
unrunnable `L` reported as passing.

---

## Dimension 4 — Gate audit (C4) — is "done" machine-defined?

**Question:** is **done** defined *only* by machine gates, or does it rest on an
agent's report of success? Are Gate A, Gate B, Gate C present and load-bearing?

The canonical gate stack (name the target's analogues):

- **Gate A — editorial approval of the plan, before code.** A *disjoint* judge
  amends, cuts, or sharpens the plan; it judges the higher-risk half before any
  source is written. **A rubber stamp here makes the upper bound fictional** — the
  approval must demonstrably alter or contest the plan, not echo it. Confirm no
  source edit ever flows from an unapproved (`DRAFT`) plan.
- **Gate B — machine-checked acceptance.** The build/compile is green; every claim
  is bound; every number is machine-generated; conservation invariants (additivity,
  standing counts, determinism re-runs) hold. This is the per-plane hard check.
- **Gate C — coverage / no-blend / coherent-and-wrong.** Each obligation clause of
  the property maps to a *passing* check; the planes are *not blended* (one plane's
  weak check standing in for another); and the gate is **calibrated by seeded
  falsifications** (Dimension 5). Gate C is the one carrying the soundness argument
  where authority is authored — confirm it is real, not a label.

**The decisive test for C4:** trace one item to `DONE` and ask *what actually
ended it*. If the answer is "the agent reported success" or "it reads well /
compiles," that is the **self-declared-done** collapse — reading well is what the
dominant failure looks like. Done must reduce to *gates passing, witnessed by
independently authored evidence.*

**Pass** = done is gate-defined; A/B/C all present and load-bearing. **Fail** =
any self-report in the done definition; a missing or vacuous gate; Gate A that
never amends; Gate C without calibration.

---

## Dimension 5 — Coherent-and-wrong probes (monitor calibration)

**Question:** does the loop actually *catch* coherent-and-wrong, or is its monitor
a rubber stamp that flags nothing?

A monitor that flags nothing has stopped checking; a monitor that flags everything
is saturated (over-claiming, or auditing a uniformly-bad population). A healthy
monitor **discriminates** — it flags a *strict, nonempty subset*.

**Procedure.**

1. **Seed plausible-but-wrong artifacts.** Plant a controlled set of
   coherent-and-wrong inputs the loop *should* catch: a valid result that proves an
   adjacent / weaker property; a doc-vs-runtime blend (compliant documentation over
   broken behaviour); an over-stated comparative claim that survives an abstract
   read but not a full-text read; a result that holds on one seed but not on a
   perturbed one. (Concrete primitives in this repo: `verify/perturbation.py`
   perturbs the anchor/seed; `verify/category_overreach.py` tests a generated
   category on every instance.)
2. **Run the loop on the seeds.** Every seed must be caught with the *right verdict
   and the right localization* — a verification run that would not have caught a
   planted falsehood has not verified anything. A missed seed *voids the run*.
3. **Flag-rate calibration.** Across the population the monitor audits, assert
   `0 < flagged < total` (the discriminating band). A permanent zero is a
   **rubber stamp**; flagging everything is **saturation**. (Primitive:
   `verify/flag_rate.py`, which asserts each monitoring plane sits in the band and
   refuses a zero external-catch count.)

**Pass** = all seeds caught with correct verdicts; every monitor in the
discriminating band. **Fail** = any missed seed; any permanently rubber-stamping
or saturated monitor.

---

## Dimension 6 — Soft-output / skill audit — VIA `sl-monitoring-sl`

**This is where the auditor depends on the `sl-monitoring-sl` skill.** State this
plainly in the report: the dimension that audits a target loop's *learned, soft
outputs* IS the `sl-monitoring-sl` pattern, invoked here, not re-implemented.

**Question:** if the target loop accumulates learned skills / heuristics, are they
*in-band* — readings the loop's own bounds do not refute on any reachable input —
or has it consolidated **coherent-and-wrong skills** (right on the common case,
silently wrong on a governed exception)?

**Procedure (delegate to `sl-monitoring-sl`):**

1. **Treat the audit as another squeeze.** The monitor's upper bound is the *base
   loop's* `U`; its lower bound is the *base loop's* executable `L`; its forbidden
   move is reading the deciding actor's rationale for the skill or editing the base
   loop's implementation. Squeeze each accumulated skill **from a disjoint base**,
   not from the actor that wrote it (its producer shares the skill's blind spot).
2. **Classify each skill by kind and run the matching check** (Gate S):
   - **ignore-signal** ("treat signal `X` as noise") — the high-risk kind; it
     *inverts* the oracle's relevance. Run the **trigger test** (perturb `X`, see
     if `L`'s verdict moves); repair by **carving** a bound-deferring exception on
     the values where ignoring `X` diverges from `L`. Preserve the valid core.
   - **defer-to-oracle** ("on case `S`, take the oracle-sanctioned action `A_S`") —
     consistent by construction; run the **validity test** (confirm `L` actually
     distinguishes `S` and sanctions `A_S`); **prune** if spurious.
3. **Discriminate.** A healthy audit leaves the defer-to-oracle skills untouched
   and flags only the over-reaching ignore-signal skills — most untouched, few
   carved. A skill monitor that flags everything or nothing is miscalibrated (ties
   back to Dimension 5).
4. **Verdicts** are Gate S's: `PASS` / `CARVE-OUT` / `REJECT (loud-fail)`. Every
   carve-out cites the exact `U` clause it defers to; carve-outs only ever make a
   skill *more* faithful to `U`, never license an action `U` forbids; every fix is
   traceable to a monitor finding. If a base loop's `L` is not runnable, report
   `DEPENDENCY UNMET` — never fake a PASS for an unaudited loop.

See `sl-monitoring-sl/SKILL.md` for the full Gate S procedure, the two worked
examples, and the non-negotiable discipline. **Do not re-derive it here — invoke
it.**

**Pass** = every accumulated skill is `PASS` or carved/pruned to in-band, with the
monitor discriminating. **Fail** = a self-judged skill store (the base loop
validating its own learned rules), an uncarved over-reaching skill, or a soft
skill silently standing in for the authoritative upper bound (the no-blend rule
pushed down one level).

---

## Dimension 7 — Stabilizer audit (each collapse mode is blocked)

**Question:** for each known collapse mode (an event where an actor relieves its
own squeeze), is the blocking stabilizer present and *load-bearing* in the target?

Walk the collapse-mode table; for each, find the structural rule that blocks it
and confirm it is real:

| Collapse mode | Symptom to look for | Blocked by |
|---|---|---|
| Self-judging | implementer edits/authors its own acceptance; tests pass suspiciously fast | forbidden moves load-bearing; physical barriers |
| Shared evidence | two actors hold identical `(U,L)`; an error propagates unchecked | the C1 disjointness audit (Dim 1) |
| Honorary barrier | internals in the judge's context; drivers mirror implementation quirks | barriers physical, not honorary (Dim 2) |
| Self-declared done | "the agent reported success" ends the item | done gate-defined (Dim 4) |
| Absorbed surprise | a local workaround; the loop's model of reality drifts | surprise is routed, never absorbed |
| Rubber-stamp approval | plans approved verbatim, instantly | editorial approval gates the plan, must amend/cut/sharpen |
| Coherent-and-wrong | a valid result proving an adjacent, weaker property | independence-is-the-soundness-argument + Gate C calibration |
| Weakened clause | "it proves now" after the obligation was quietly softened | strictness has a safe direction (stricter, never weaker) |
| Regression by rationalization | "that diff is expected" | conservation laws rerun after every item |
| Vacuous acceptance | a proof of a vacuous / adjacent theorem; an empty obligation set passes | Gate C axiom/coverage audit (each obligation clause maps to a passing check) |
| Unpinned reality | design built on assumed tool behaviour | pin reality before building on it |
| Scope blur | silent over-claiming; unclassified escape hatches | honest scope is a deliverable (NOT-claims, residual ledger) |
| Orphan change | an edit with no plan, no gap, no authority behind it | traceability is an acceptance criterion |

**The barrier ablation is the master stabilizer test.** Run the target with the
barrier *on* and *off*: with the barrier on the squeeze should catch the seeded
coherent-and-wrong implementers; with the barrier off (the exerciser anchored to
the implementation) the catch rate collapses. A loop whose catch rate does *not*
move when you remove the barrier never had a load-bearing barrier — the stabilizer
was decorative.

**Pass** = every collapse mode has a present, load-bearing blocker; the barrier
ablation moves the catch rate. **Fail** = any unblocked mode, or any "blocker"
that is documentation rather than structure.

---

## Dimension 8 — The irreducible limit (route to a disjoint base)

Name this honestly: **an internal audit cannot self-certify the residual.** Where
authority is *authored* (no external spec to diff against), the only defense
against coherent-and-wrong is the independence of the judge from the producer —
and an audit run *by the loop's own actors* shares the loop's blind spot exactly
as a self-judged skill does. Two residuals always escape internal mechanization:

- **Soft-vs-soft faithfulness.** "Is the framing / interpretation faithful to the
  evidence?" has no executable lower bound; no machine gate refutes "the summary
  over-emphasizes X." This must be routed to a **disjoint editorial judge** (the
  standing Gate A), with a *current* review on file (a recorded review whose hash
  matches the artifact as it stands now — a stale review is no review). Primitive:
  `verify/claim_consistency.py` mechanizes only the *return of a known* framing
  defect; `verify/editorial_gate.py` enforces that a fresh disjoint judgment
  exists. Coverage of the mechanized part is a *floor, not a ceiling*.
- **Self-description drift.** A loop can go coherent-and-wrong *about itself* — its
  apparatus changes but its description of its apparatus does not
  (`verify/apparatus_described.py` catches the named-vs-present proxy; *accurate*
  description still needs the disjoint judge).

**Routing rule.** The disjoint base should be **cross-provider or human** — a
same-provider-family judge shares the author's blind spot and counts only as
*partial* disjointness. Capability and disjointness are *different axes* and trade
off: the gold standard is a judge that is *both capable and cross-provider*; a
truly cross-provider but weak judge is recorded **non-authoritative** (it must pass
known-contradiction / known-consistent controls first), and a capable same-family
judge is recorded **partial**. Report which you have and what is still pending —
*you cannot delete the disjoint reviewer, only make its bookkeeping mechanical.*

---

## Dimension 9 — Output: the audit report

Produce a structured report, not a verdict. Form:

```
SL AUDIT — <target loop name>           date: <YYYY-MM-DD>

PER-DIMENSION FINDINGS
  D1 Disjointness (C1)        PASS | FAIL | PARTIAL   — <one line + evidence>
  D2 Barrier (C3)             PASS | FAIL | PARTIAL   — physical or honorary? <probe result>
  D3 Lower bound (oracle)     PASS | FAIL | DEP-UNMET — disjoint, immutable, runnable?
  D4 Gates / done (C4)        PASS | FAIL             — Gate A/B/C present & load-bearing?
  D5 Coherent-and-wrong       PASS | FAIL             — seeds caught? flag rate in band?
  D6 Skills (via sl-monitoring-sl)  PASS | CARVE | REJECT  — Gate S verdicts per skill
  D7 Stabilizers              PASS | FAIL             — collapse modes blocked? barrier ablation moved?
  C2 Catchability             (implied by D1+D5)      — every char. failure caught by another actor?

SEVERITY
  CRITICAL  — structural: self-certifying actor, no executable L, honorary barrier
              on a load-bearing edge, self-declared done. The loop is collapsing.
  MAJOR     — a present-but-weak gate, a miscalibrated monitor, an uncarved
              over-reaching skill, a missing stabilizer.
  MINOR     — bookkeeping: stale editorial review, undescribed apparatus, traceability gaps.

DISJOINT-BASE ROUTING (the residual)
  - Soft-vs-soft faithfulness  -> <cross-provider | human judge>; status: <on file / stale / pending>
  - Self-description accuracy   -> standing Gate A; status: <...>
  - Any DEPENDENCY-UNMET oracle -> <named>, NOT certified by this audit.
```

**Discipline for the report itself (the audit obeys the squeeze it audits):**

- **Loud-fail, never approximate.** An undecidable dimension is reported
  `DEPENDENCY UNMET` or routed to the disjoint base — never quietly passed.
- **Ground every finding.** Cite the delegation prompt / oracle / gate that
  evidences it; a finding with no evidence is hearsay.
- **Safe direction.** When unsure, downgrade the loop's claimed soundness, never
  inflate it — understating a loop's health is a style choice; overstating it is
  the dominant failure wearing its best suit.
- **Do not self-certify the residual.** The audit's own soft-vs-soft judgments are
  themselves routed to a disjoint base; an internal audit that claims to have
  certified everything has just demonstrated the failure it was hunting for.
