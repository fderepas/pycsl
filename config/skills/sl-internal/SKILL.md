---
name: sl-internal
description: A self-contained explainer of how the Squeeze Loop (SL) strategy works — the construction that makes a multi-actor loop converge on a correct deliverable rather than on a plausible-looking one. It defines the squeeze (every actor pinned between a soft upper bound and a hard, executable lower bound), the coherent-and-wrong failure it targets, the load-bearing disjointness principle (each actor answers to a different authority pair, with physical context barriers), the canonical cast of roles, the gates (A editorial, B machine-checked, C coverage / no-blend / coherent-and-wrong, S skill-consistency), the loop mechanics (DRAFT→APPROVED→DONE handshake, gap documents, gate-defined done), the terrain archetypes (where truth lives), the stabilizers against collapse, and the compliance conditions. It is domain-generic and stands alone — no external sources. Use it whenever you need to understand or explain the strategy from first principles. Trigger phrasings include "how does a squeeze loop work", "explain the squeeze loop strategy", "what is the disjointness principle", "what are the gates / the canonical cast", "what is coherent-and-wrong", "why is done gate-defined", "what are the terrain archetypes", "what are the stabilizers".
---

# The Squeeze Loop (SL) strategy

This skill explains the whole strategy from first principles. It is generic: it
names no domain and no specific use case, and it stands entirely on its own. Read
it when you need to understand *why* the strategy works, not just how to run it.

## The squeeze (one paragraph)

A **squeeze loop** holds every actor between an **upper bound** and a **lower
bound**. The upper bound is a *citable, normative soft truth*: a norm, standard,
or specification carried in natural language — authoritative but
interpretation-laden — that fixes the **strongest claim the actor may make**. The
lower bound is an *executable hard truth*: a runnable oracle whose verdict is
mechanical and interpretation-free, and which the actor **cannot alter**. A
deliverable is **in-band** only when it is *a reading of the upper bound that the
lower bound does not refute* — faithful to the soft truth (claims no more than it
licenses) and consistent with the hard truth (running the oracle does not
contradict it). Above the band is over-claiming; below it is fidelity to nothing
but itself. Neither bound suffices alone: the hard truth cannot say what *ought*
to be produced, and the soft truth cannot say what *is* produced. The squeeze
exists to bind one to the other.

## Coherent-and-wrong — the failure being targeted

The dominant failure is not gibberish; it is fluency that is false.
**Coherent-and-wrong** is a *plausible interpretation of the soft upper bound that
the hard lower bound contradicts* (or, dually, an artifact that satisfies the hard
check while betraying the soft intent). It reads as correct, passes its author's
own checks, and still misses the intended property. A loop made only of agents
that grade their own work will converge on exactly this: a result that *looks*
done. The whole strategy is built to make coherent-and-wrong catchable by someone
other than the actor that produced it.

## The disjointness principle (load-bearing)

A single squeeze is not enough, because an actor can be wrong inside its own band:
its evidence base has a characteristic blind spot, and self-checking shares that
blind spot. The fix is **disjointness**:

> Every actor answers to a **different** `(upper, lower)` pair, and the pairs are
> chosen so that the **intersection** of all in-band sets is the correct
> deliverable, while **no single actor's evidence base is sufficient** to certify
> it on its own.

Two pairs that are identical define one actor, not two — a new role is justified
only by a **new evidence base**, never by workload. Disjointness has a consequence
the strategy depends on: each actor's characteristic blind spot is caught by
**another actor that cannot share it**, because that other actor reads from a
different source. A corruption of any single source, or any single actor's blind
spot, cannot propagate silently, because no other actor reads from it.

For disjointness to be real and not aspirational, the separation must be
**physical, not honorary**:

- **Honorary barrier** — the actor *has* the forbidden evidence in its context and
  is merely *instructed* not to use it. An actor that holds the internals in
  context will eventually use them; honorary barriers fail.
- **Physical barrier** — the forbidden evidence is **absent from the actor's
  context** at delegation time. Each actor starts from fresh context containing
  exactly its authorities and the public interfaces it must exercise; the evidence
  it is denied (most importantly, the implementation, for any actor that judges it)
  is simply not there. If a judge needs to know how the implementation behaves, it
  *runs* the implementation and reads the verdict — it never reads the internals.

## The canonical cast

A single squeeze brackets one actor; a real task needs several. The standard cast
is five roles, each carrying its own squeeze and a **forbidden move** — the
role-crossing action that would relieve its own pressure. The forbidden moves are
load-bearing, not hygiene.

- **Coordinator** — builds approvals, sequencing, and gate verdicts. Squeezed from
  above by the binding plan/spec; from below by the gates' machine output.
  *Forbidden:* editing the work product; approving a plan it has not editorially
  judged.
- **Property author** (upstream) — builds the precise specification: the obligation
  clauses, the one failure the negative case must catch, the explicit NOT-claims.
  Squeezed from above by the external category or flagship use case; from below by
  **expressibility** — every clause must be dischargeable by *some* mechanism.
  *Forbidden:* proposing the implementation or reading its internals.
- **Implementer** — builds the item plus its documentation. Squeezed from above by
  the spec's strongest mandated claim; from below by shipped machinery, standing
  invariants, and **total additivity** (no pre-existing output may change).
  *Forbidden:* weakening a clause or a gate to land; touching the acceptance
  evidence.
- **Exerciser** — builds the positive/negative acceptance evidence. Squeezed from
  above by the spec's acceptance clauses and the documented surface *only*; from
  below by what actually passes or proves when run. *Forbidden:* reading the
  implementation or any diff.
- **Probe** — builds minimal experiments with recorded verdicts, one claim per
  probe. Squeezed from above by the single design claim under test; from below by
  the tool's *actual* behaviour. *Forbidden:* implementing anything — a probe
  writes a verdict, never a fix.

## The gates

Done is decided by gates, never by an actor's self-report. Each item passes
through them.

- **Gate A — editorial approval (judgment, not machine output).** The coordinator
  validates the plan/property against the **upper bound** by *judgment*: it must
  amend, cut, or sharpen, never merely stamp. A rubber stamp makes the upper bound
  fictional. This gate adjudicates against the soft truth — the part no machine can
  fully decide.
- **Gate B — machine-checked acceptance (the hard truth).** A mechanical check:
  positives pass; negatives fail at the *named site* violating the *named clause*;
  the **standing invariant** is rerun after every item (e.g. byte-identical output
  for every pre-existing input, plus a determinism re-run), which turns regression
  into a definitional impossibility — *"if your change alters an existing output,
  your change is wrong by definition."*
- **Gate C — coverage / no-blend / coherent-and-wrong guard.** The guard against
  the dominant failure: *each obligation clause of the property maps to a specific
  passing check*, and the thing actually proved is checked to be *the property
  intended* (not an adjacent, weaker one). Where external ground truth exists, Gate
  C is machine-checked; where it does not, it is defended by **author
  independence** — the property's author and the exerciser never saw the
  implementation. It also enforces **no-blend**: distinct planes of truth must
  never silently substitute for one another (a weak check on one plane standing in
  for a strong claim on another).
- **Gate S — skill-consistency (different cadence).** Fires not per item but
  whenever the loop *accumulates a learned skill* — a soft heuristic an actor
  consolidated from its own caught errors. Because the actor that produced a skill
  shares its blind spot, the skill is checked by a **monitor squeeze** holding a
  disjoint evidence base (the loop's own upper bound and its executable lower bound
  used as an oracle). The monitor differential-tests each skill and returns
  **pass**, a **carve-out** (a narrowing exception deferring to the upper bound
  where the skill over-reaches, preserving its valid core), or **reject**. Gate S
  is the no-blend rule applied to a loop's own learned outputs: a soft *skill* may
  never silently stand in for the upper bound — a squeeze monitoring a squeeze.

## Loop mechanics

Work circulates through **paired traceability documents** and a **status
handshake**:

- A **forward plan** is opened at **`STATUS: DRAFT`**, set to **`APPROVED`** only
  after Gate A's editorial judgment, and to **`DONE`** only when the gates pass. No
  edit to the work product ever happens from a `DRAFT` — the plan is the
  higher-risk half and is judged before anything is built.
- The **backward motion** is a **gap document**, written by whichever actor
  observed a divergence (a failing acceptance line, a surprising probe verdict, an
  oracle that refuses the claimed contribution). It carries the same number as the
  plan that answers it, re-enters the handshake, and is the only legitimate way to
  renegotiate a claim — *in the open*, never as a silent local workaround.
- **Done is defined only by the gates.** An item is done iff the fixed set of
  machine-checked gates passes, witnessed by independently authored evidence. No
  actor's self-report contributes to the definition: "the agent reported success"
  never ends an item, and "it reads well / it looks done" is exactly what the
  dominant failure looks like.

## Terrain archetypes — where the truth lives

The loop **topology is invariant**; the *materials* of each squeeze are not. The
coordinator's first act on a new instance is epistemic: locate where truth lives.
Three terrains recur.

- **A — Transcription (an external authority exists).** Some external written
  specification already states what *correct* is. The upper bound is that
  specification; the lower bound is execution of the real thing. The dominant
  failure is improvisation / unfaithful transcription. The soundness load rests on
  the machine gate plus the standing invariant: every claim recomputes against
  frozen ground truth, so a wrong result cannot survive re-execution.
- **B — Authored authority (no external authority).** No external spec exists to
  diff against; the authority is **authored upstream** and anchored to a flagship
  use case. The dominant failure is coherent-and-wrong. With nothing external to
  diff against, the soundness load rests on the coherent-and-wrong guard
  **defended by author independence** — the gate is only as sound as the barrier
  that keeps the author and exerciser from ever seeing the implementation.
- **C — Split planes (separate authorities).** Two (or more) planes of truth each
  with its own authority and ground truth, plus a precedence rule. The dominant
  failure is **blending**: one plane's weak check standing in for the other's
  strong claim. The soundness load rests on a **no-blend cross-check**: each plane
  is verified separately and the planes must agree, so neither can mask the other.

Real systems mix archetypes per work item; the archetype decides what the bounds
are made of, which failure dominates, and which gate carries the soundness
argument. The same topology shifts its weight to a different gate per instance —
that is what "rebuild the squeeze from local materials" means.

## Stabilizers — anti-collapse rules

A **collapse** is any event in which an actor relieves its own squeeze. The
stabilizers are structural rules that block each collapse mode; each is paired
below with the mode it blocks.

- **Forbidden moves are load-bearing.** Each role's negative constraints (never
  edit the drivers, never read the diff, never implement a fix, never touch source)
  are what keep the squeeze from collapsing. *Blocks: self-judging.*
- **Information barriers are physical, not honorary.** Separation is enforced by
  what is in the delegation context — fresh context, surface and acceptance lines
  only — not by asking an agent to refrain. *Blocks: honorary barrier.*
- **Done is gate-defined, never self-declared.** Done is machine gates passing,
  witnessed by independent evidence; self-assessment is never evidence. *Blocks:
  self-declared done.*
- **Conservation laws bound the blast radius.** A standing invariant (total
  additivity, standing counts, determinism re-runs) is rerun after *every* item.
  *Blocks: regression by rationalization.*
- **Surprise is routed, never absorbed.** A surprising verdict or failing line
  becomes a gap document that re-enters the handshake; a local workaround
  desynchronizes the loop's model of reality from reality. *Blocks: absorbed
  surprise.*
- **Pin reality before building on it.** One claim per probe, one minimal
  experiment, one recorded verdict; feasibility proven on a minimal instance before
  machinery is built. *Blocks: unpinned reality.*
- **Specify the implicit base before extending it.** Transcribe existing de facto
  behaviour into the references before adding anything, and verify the transcription
  by independent prediction. *Blocks: unspecified base.*
- **Editorial approval gates the plan, before code.** Approval judges the
  higher-risk half and must amend, cut, or sharpen; no edit from a `DRAFT`.
  *Blocks: rubber-stamp approval.*
- **Honest scope is a deliverable.** Explicit NOT-claims, residual ledgers, and the
  classification of every escape hatch make what was *not* proven as legible as
  what was; "specified, not solved" and "loud-fail, never an approximation" are
  first-class dispositions. *Blocks: scope blur.*
- **Strictness has a safe direction.** The implementation may be *stricter* than
  the authority, never weaker; divergence-by-strictness is recorded and legitimate,
  divergence-by-weakness is a bug. *Blocks: weakened clause.*
- **Sequence by mechanism reuse; parallelize only across independence.** Each item
  rides machinery the previous one hardened; chains are sequential internally and
  parallel only when they share no evidence base and no deliverable. *Blocks:
  unsequenced parallelism.*
- **Traceability is itself an acceptance criterion.** Every change traces to an
  approved plan, every plan to the gap or authority section that motivated it; an
  unexplained change is, by construction, a violation. *Blocks: orphan change.*
- **Where authority is authored, independence is the soundness argument.** With no
  external spec to diff against, the only defense against coherent-and-wrong is that
  the property's author and exerciser never saw the implementation; the design must
  name this explicitly and protect it. *Blocks: shared evidence between actors who
  must disagree.*

## Compliance conditions

A workflow is **squeeze-loop compliant** when all four hold:

1. **Disjointness.** The authority pairs are pairwise distinct and chosen so their
   intersection is the correct deliverable while no single pair suffices to certify
   it.
2. **Catchability.** For every actor and every characteristic failure that survives
   its own squeeze, there exists *another* actor from whose pair that failure is
   detectable.
3. **Physical barriers.** At delegation time each actor's context contains exactly
   its authorities and the interfaces it must exercise; denied evidence is *absent*,
   not merely off-limits by instruction.
4. **Gate-defined done.** An item is done iff the fixed set of machine-checked
   gates passes; no actor's self-report contributes to the definition.

Disjointness is the centerpiece and the condition most often missing from ordinary
pipelines. Under disjointness plus catchability, no single corrupted source or
blind spot can propagate silently — which is the entire point of the strategy.
