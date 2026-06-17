---
name: sl-monitoring-sl
description: Specifies how one squeeze loop monitors another squeeze loop — squeezing the monitored loop's soft outputs (especially its accumulated skills / learned heuristics) against that loop's own upper and lower bounds, from an independent evidence base; it classifies a skill by kind (ignore-signal vs defer-to-oracle), runs the matching consistency check, and repairs by carving over-generalized skills with bound-deferring exceptions or pruning spurious ones. Use when a loop accumulates or consolidates skills that may over-reach; when you need a meta-loop or monitor that audits a base loop's learned rules for contradictions with its spec; when a learned heuristic seems to conflict with the governing policy; or when reasoning about the "disjointness principle applied to skills." A key execution principle: even when the monitor loop is itself launched as an agent, it must launch the observed (base) loop as a sub-agent one level deeper — never run it inline — because the delegation boundary makes the author-separation barrier physical (the monitor sees only returned soft outputs, never the base loop's rationale) and keeps the monitor's context bounded so it scales. Trigger phrasings include "a loop monitoring a loop", "monitor the squeeze loop", "check a skill against the upper bound", "the skill contradicts the spec", "carve out an exception", "prune a spurious skill", "who audits the learned skill", "skill-consistency gate", "should the monitor run the observed loop as a sub-agent", "run the base loop as a sub-agent of the monitor".
---

# A squeeze loop monitoring a squeeze loop

This skill specifies a meta-pattern: how a **monitor loop** audits a **base loop**'s
*soft, learned outputs* — chiefly the **skills** a base loop accumulates — by squeezing
them against the base loop's own bounds, from an evidence base the base loop's actors
do not have. It is generic: it names no domain, no instance, no concrete policy.

## Background: a squeeze loop in one paragraph

A **squeeze loop** holds every actor between an **upper bound** `U` (a citable,
normative *soft* truth — the strongest claim an actor may make) and a **lower bound**
`L` (an executable *hard* truth — a runnable oracle whose verdict the actor cannot
alter). A deliverable is **in-band** only if it is a reading of `U` that `L` does not
refute. The load-bearing rule is **disjointness**: every actor answers to a *different*
`(U, L)` pair, chosen so the intersection of all constraints is the correct deliverable
while *no single actor's evidence base suffices to certify it* — so each actor's
characteristic blind spot is caught by another actor that cannot share it.

## What a "skill" is here, and why it is dangerous

A **skill** is a *soft, learned heuristic* a base loop's **deciding actor** consolidates
to avoid repeating a class of caught error. It is not the spec and not the oracle; it is
an actor's compressed memory of its own failures. Two facts make it dangerous:

1. **It is learned from one signal.** The deciding actor consolidates skills only from
   the errors *it was caught making*. Its evidence base is one-sided, so its skills
   tend to **over-generalize** in the only direction that signal points.
2. **Its producer cannot audit it.** The same blind spot that produced an
   over-general skill prevents the producer from seeing the over-generalization. An
   actor checking its own skill is exactly the self-judging the squeeze forbids.

So a consolidated skill can be **coherent-and-wrong**: it reads as sound advice and is
right on most inputs, yet on some reachable input it prescribes an action `U` overrides.

## The disjointness principle, applied to skills

Disjointness says: no actor certifies its own work; each blind spot is caught by an
actor with a *different evidence base*. **Apply it to skills:**

> A skill is **in-band only if it is a reading the bounds do not refute on any reachable
> input.** Because the skill's producer shares the skill's blind spot, the check must be
> performed by a **different actor whose evidence base is `U` and `L`** — the upper bound
> and the executable oracle — *not* the deciding actor's own reasoning.

The deciding actor holds "what I was caught doing." The monitor holds "what the spec
mandates" (`U`) and "what actually happens when run" (`L`). These are *disjoint evidence
bases*. The carve-out — the exception that repairs an over-general skill — can only be
derived by the actor holding `U` and `L`, never by the actor that wrote the skill. This
is the **no-blend rule** (distinct planes of truth must never silently substitute for
one another) pushed down one level: a soft *skill* must never silently stand in for the
soft-but-authoritative *upper bound*.

## The monitor is itself a squeeze loop

Monitoring a loop is not "review"; it is **another squeeze**. The monitor loop is held
between its own bounds:

- **Monitor's upper bound** = the *base loop's* `U` (the spec the skill must not
  contradict). The monitor may claim no more than "this skill is/ isn't a reading `U`
  refutes."
- **Monitor's lower bound** = the *base loop's* `L` (the executable oracle), used as a
  differential-testing comparator against the skill.
- **Monitor's forbidden move** = reading the deciding actor's rationale for the skill, or
  editing the base loop's implementation. It judges the skill against `U`/`L` only, and
  emits a verdict (and a carve-out), never a silent fix.

So "a squeeze loop monitors a squeeze loop" = the monitor squeezes the base loop's
*skills* between the base loop's *own* `U` and `L`, from outside the base loop's actors.

## Run the observed loop as a sub-agent of the monitor (key principle)

**Even when the monitor loop is itself launched as an agent, it must launch the
*observed* (base) loop as its own sub-agent — one delegation level deeper — never run the
base loop inline in the monitor's own context.**

```
monitor SL            (agent)         <- context accumulates only the base loop's RETURNED soft outputs
  └─ observed SL      (sub-agent)     <- all of the base loop's internal work stays HERE
       └─ base actors (sub-sub-agents)
```

This is load-bearing on two axes that turn out to be the *same boundary* seen twice:

- **It makes the barrier physical, not honorary.** The monitor's forbidden move is
  *reading the deciding actor's rationale*. Running the base loop as a sub-agent enforces
  that by construction: the base loop's reasoning, its oracle runs, its deliberation all
  live and die in the sub-agent's context and **never cross back** — only its *soft
  outputs* (the consolidated skill, the inferred contract, the verdict) return. The
  monitor literally cannot see the rationale, so it cannot judge against it. **The
  sub-agent boundary IS the barrier.**
- **It keeps the monitor's context bounded, so the monitor scales.** Because only the
  small returned outputs accumulate in the monitor's context (not the base loop's heavy
  work), one monitor can audit a long run of base-loop outputs without its own window
  overflowing.

Nesting is the mechanism: `main → monitor (agent) → observed (sub-agent) → actors`. Where
the harness supports nested delegation, **prefer this over a flat, inline monitor** — a
flat monitor that runs the base loop in its own context both *sees the rationale* (a
barrier leak) and *fills its own window* (no scale).

**Bounded, not zero.** The monitor's context still accrues one summary per observed
output; for a very large run, chunk the work and summarize-and-forget between batches, or
move the *coordinator* off any LLM context entirely (deterministic orchestration) so only
the leaf actors hold a context window.

## When to use / when not to use

**Use** when a base loop accumulates or mutates skills/heuristics that act on inputs
governed by a spec; when you are designing a meta-loop to audit a base loop; when a
learned rule may conflict with the governing upper bound.

**Do not use** to author skills from scratch, to improve a skill's *wording or
structure* (that is form, not consistency — use a polishing skill), or where there is no
executable `L` to differential-test against (then the check degrades to a manual
`U`-only audit and must say so).

## Gate S — the skill-consistency check

Run this whenever the base loop proposes or mutates a skill. A proposed skill enters the
base loop's store only after Gate S returns one of:

- **PASS** — the skill agrees with `U` (verified against `L`) on all sampled inputs.
- **CARVE-OUT** — a narrowing exception, cited to the part of `U` it defers to, fed back
  into the skill; the skill is kept minus its contradicting region.
- **REJECT (loud-fail)** — the skill cannot be reconciled (wrong on (almost) all inputs,
  or carving would leave nothing); flag and discard, never silently keep.

Inputs to Gate S: the proposed skill rule(s); `U`; `L`. **Not** the deciding actor's
notes.

## Skills make a relevance claim — match the check to the skill kind

Every skill is, at bottom, a **claim about the oracle's relevance structure** — which
inputs matter to the verdict, and how. Gate S checks that claim against the oracle's
*actual* relevance. Two kinds recur; they need different checks and different repairs:

| skill kind | the relevance claim | how it fails | check | repair |
|---|---|---|---|---|
| **ignore-signal** ("treat signal `X` as noise") | "`X` is irrelevant to the verdict" | `X` *is* relevant — the skill suppresses an input `U` uses | **trigger test**: perturb `X`, see if `L`'s verdict moves | **carve-out** (defer to `U` on `X`) |
| **defer-to-oracle** ("on case `S`, take the oracle-sanctioned action `A_S`") | "`S` is a real decision point and `A_S` is what `U` mandates there" | `S` is not a real decision point, or `A_S` is stale / spurious | **validity test**: confirm `L` actually distinguishes `S` and sanctions `A_S` | **prune / correct** the spurious rule |

The crucial asymmetry between the two kinds — the reason a monitor needs both checks:

- **ignore-signal skills are the high-risk kind.** They *invert* the oracle's relevance
  judgment ("`U` reacts to `X`; I will pretend it does not"), so they over-generalize
  into territory `U` governs and produce silent contradictions. This is where carve-outs
  come from.
- **defer-to-oracle skills are consistent by construction.** They *follow* the oracle, so
  the only way they go wrong is by referencing something the oracle does not sanction (a
  non-existent decision point, a dead action). They almost always PASS; their check is a
  spuriousness guard, not a contradiction hunt.

So a healthy monitor over a *suite* of base loops **discriminates**: it leaves the
defer-to-oracle skills untouched and flags only the ignore-signal skills that suppress a
live signal. A monitor that flags everything — or nothing — is miscalibrated.

## Check 1 — ignore-signal skills (trigger test → carve-out)

For each rule `R` that says "treat `X` as noise":

1. **Decompose.** Identify the signal class `R` ranges over.
2. **Differential-test against the oracle.** For each value `v`, construct or sample an
   input isolating `v` and compare the action `R` implies (ignore `v`) to the action `L`
   returns. (Differential testing with `L` as comparator.)
3. **Localize divergence.** Let `V` = the values where ignoring `v` diverges from `L`.
4. **Carve.** If `V` is a strict, small subset: keep `R` on its complement and add an
   exception deferring to `U` on `V`, citing the clause: *"…treat `X` as noise.
   **Exception: on `V`, defer to `U` → <bound-mandated action>.**"* (Preserve the valid
   core.)
5. **Reject.** If `V` is most of the class or the complement is empty, REJECT and log.

The producer could not run this: step 2 needs `U` and `L`, which it does not hold; step
3 isolates the very case it was blind to.

## Check 2 — defer-to-oracle skills (validity test → prune)

For each rule `R` that says "on case `S`, take the oracle-sanctioned action `A_S`":

1. **Confirm `S` is a real decision point.** Run `L` inside and outside `S`; if `L`'s
   verdict does not actually turn on `S`, `R` defends a non-existent distinction →
   **prune** it (spurious skill).
2. **Confirm `A_S` is oracle-sanctioned.** Check `A_S` is an action `L` actually produces
   or accepts for `S` (not stale, not invented). If not → **correct or prune**.
3. **PASS** if `S` is real and `A_S` is what `U` mandates — the skill merely follows the
   oracle, which is in-band by construction.

Both checks resolve to the same Gate S verdicts (PASS / CARVE-OUT / REJECT); which check
to run is chosen by the skill's kind, and an adapter supplies the per-base-loop oracle.

## Discipline (non-negotiable)

- **Grounded.** Every carve-out cites the exact part of `U` it defers to.
- **Preserve the valid core.** Carve (narrow); do not discard when a valid complement
  exists. Most of a learned skill is usually right.
- **Loud-fail.** An irreconcilable skill is rejected and logged, never silently kept.
- **No blend / author separation.** The monitor judges from `U` and `L`, never from the
  producer's account of why it learned the skill.
- **Physically isolated.** Run the observed loop as a **sub-agent**; the monitor sees only
  its returned soft outputs, never its in-context rationale — the delegation boundary
  enforces author separation by construction (see *Run the observed loop as a sub-agent of
  the monitor*).
- **Safe direction only.** A carve-out may only make a skill *more* faithful to `U`
  (narrower); it may never license an action `U` forbids.
- **Traceable.** Record each carve-out or prune (which skill, which clause, which inputs
  revealed the divergence) so the fix demonstrably *arose from a monitor finding*, not
  intuition.
- **Oracle availability is honest, not assumed.** Each base loop's `L` arrives in a
  different form (a pure function, a committed verdict cache, a live datastore, a
  conformance suite). If a base loop's `L` is not runnable, report it
  (DEPENDENCY UNMET) — never fake a PASS for an unaudited loop.
- **Match the check to the kind.** Run the trigger test on ignore-signal skills and the
  validity test on defer-to-oracle skills; applying the wrong check (e.g. a trigger test
  to a "do-X-correctly" skill) yields false negatives.

## Worked example A — an ignore-signal skill (the high-risk kind, carved)

A base loop's deciding actor keeps getting caught over-acting whenever the input carries
a **pressure signal** drawn from a class `P = {p1, p2, …, pk}`. It consolidates the
skill: *"treat any signal in `P` as noise; ignore it and decide on the case facts."*

Gate S decomposes the rule over `P` and differential-tests each `pi` against `L`:

- For `p1 … p(k-1)`: `L` confirms the signal is **not** decision-relevant — ignoring it
  matches the oracle. The skill is right here.
- For one member `p*`: `U` makes `p*` itself a **decision trigger** (a specific mandated
  action `A*`). The oracle returns `A*`; the skill returns "ignore → some fact-based
  action ≠ `A*`." **Divergence localized to `V = {p*}`.**

Gate S emits the carve-out:

> *"Treat signals in `P` as noise and decide on the facts. **Exception: `p*` is itself a
> trigger under `U` → `A*`; do not ignore it.**"*

The carved skill now matches `U` everywhere; the residual error vanishes. Crucially the
carve-out came from the **monitor** (holding `U` and `L`), because the deciding actor —
trained only on its own caught over-actions — had no signal that `p*` must trigger `A*`,
and so could never have produced the exception itself.

## Worked example B — defer-to-oracle skills (the common kind, pass clean)

In a parallel base loop the actor learns *"for case `S`, use the oracle-sanctioned
action `A_S`"* (it was caught using a wrong-but-plausible action, and consolidated the
certified one). Gate S runs the **validity test**: it confirms `L` genuinely
distinguishes `S` (the case is a real fork, not a phantom) and that `A_S` is what `L`
produces there. It does — the skill simply *follows* the oracle — so it **PASSES** with
no change. This is the expected outcome for defer-to-oracle skills: across a suite of
base loops, most skills are of this kind and pass clean, while the ignore-signal skills
(example A) are the ones that need carving. That contrast — most untouched, few flagged
— is the monitor **discriminating**, which is how you know it is calibrated rather than
rubber-stamping or crying wolf.

## Failure modes this prevents

- **Self-judged skills.** A loop validating its own learned rules — the same blind spot,
  doubled.
- **Over-generalized heuristics** that are right on the common case and silently wrong on
  a governed exception (coherent-and-wrong at the skill level).
- **Form-over-content fixes.** Reformatting or sharpening a skill whose *content*
  contradicts `U` — which can make a clearer-but-wrong rule fire more reliably. Form
  tools cannot do Gate S's job; only a `U`/`L` squeeze can.
