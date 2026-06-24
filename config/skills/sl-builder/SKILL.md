---
name: sl-builder
description: >-
  Defines how to construct and package Squeeze Loop (SL) artifacts, ensuring
  deterministic builds, reproducible environments, and correct integration of
  monitoring components. Use when generating an SL implementation or CI pipeline.
  the answers into a roles+bounds+barriers+gates+loop-steps plan. Use when the
  user says any of: "draft a plan to generate a squeeze loop", "draft an SL
  validation plan", "build an SL strategy for X", "design a squeeze loop for my
  problem", "help me set up a squeeze loop", "SL validation plan for C code with
  Frama-C", "an SL that monitors another SL", "nested squeeze loop / monitor of
  a monitor". Action-oriented: figure out what is known, ASK the missing
  interview questions, then OUTPUT a plan in the template.
---

# SL Builder — interview a human, then draft a Squeeze Loop plan

This skill turns a vague wish ("I want correctness for X") into a concrete
**Squeeze Loop (SL)** plan. It does two things, in order:

1. **Interview.** Ask the structured questions below that the human has *not*
   already answered, to elicit the SL design.
2. **Draft.** Synthesize the answers into a plan using the template in
   *How to draft the plan*.

Be action-oriented. When invoked: read the request, mark each interview slot as
KNOWN or MISSING, ASK only the MISSING ones (batched, grouped), then DRAFT. If
the human is impatient or under-specifies, draft with explicit `ASSUMPTION:`
markers and a short list of open questions appended — never stall.

## One-paragraph background (so this skill stands alone)

A **squeeze loop** holds every actor between an **upper bound** `U` — a citable,
normative **soft** truth (a spec/standard/policy/contract in natural or
semi-formal language; the strongest claim an actor may make) — and a **lower
bound** `L` — an executable **hard** truth (a runnable oracle whose verdict the
actor cannot alter: a test passes or fails, a proof obligation discharges or it
does not). A deliverable is **in-band** iff it is a reading of `U` that `L` does
not refute. **Coherent-and-wrong** is the dominant enemy: a plausible reading of
`U` that `L` contradicts (or an artifact that passes the hard check while
betraying the soft intent). The load-bearing rule is **disjointness**: every
actor answers to a *different* `(U,L)` pair, chosen so the **intersection** of
all in-band sets is the correct deliverable while **no single actor's evidence
base certifies it** — so each actor's blind spot is caught by another actor that
cannot share it. Barriers are **physical** (in the delegation context), not
honorary. **Done** is gate-defined, never self-declared.

The canonical cast (five roles; add a role only for a *new evidence base*):
**coordinator** (judge/sequencer; never edits source or rubber-stamps),
**property/spec author** (writes `U` from the requirement; never sees the
implementation), **implementer** (builds the artifact to satisfy `U`; never
touches the acceptance evidence), **exerciser/verifier** (authors acceptance
evidence from the spec+surface only; never reads the implementation),
**probe** (one experiment, one recorded verdict; writes verdicts, never fixes).

---

## 1. The interview — questions to elicit an SL design

Group the questions; explain *why* each matters; ask only what is MISSING.

### Group 1 — The deliverable and "correct"
- **What is the deliverable?** (verified C, a paper, an agent policy, a dataset…)
- **What does "correct" mean for it, operationally?** Push for a definition that
  could in principle be *checked*, not admired. ("Reads well" is what the
  dominant failure looks like.)
- **What is the dominant failure you fear?** Name the *coherent-and-wrong*
  specific to this problem (see Group 7).

### Group 2 — The upper bound `U` (soft normative authority)
- **What is the authority every claim answers to?** Spec, standard, policy,
  requirement, contracts (e.g. ACSL), a CFP, a global interface spec.
- **Does it exist externally, or must it be authored?** This sets the **terrain
  archetype**:
  - **A — transcription:** an external written spec already exists; `U` is on
    disk; dominant failure is unfaithful transcription/improvisation.
  - **B — authored authority:** no external spec; `U` must be *authored upstream*
    by someone who never sees the implementation; dominant failure is
    coherent-and-wrong, and **author independence is the entire soundness
    argument**.
  - **C — split planes:** correctness divides across two+ planes, each with its
    own `(U,L)` and a precedence rule; dominant failure is **blending** (one
    plane's weak check standing in for the other's strong claim).
- **If it must be authored — who authors it, and from what?** (the requirement,
  a standard, the upstream interface).

### Group 3 — The lower bound `L` (executable oracle)
- **What runnable process renders a verdict the actor cannot argue with?**
  A prover/checker (Frama-C/WP discharge), a test suite, a runtime, a reference
  implementation, gold tests, a measure, a type checker, link/integration tests.
- **Does it exist or must it be built first?** If it must be built, it is the
  *first work item* (pilot before machinery; pin reality before building on it).
- **Is the verdict mechanical and interpretation-free?** If not, it is not yet
  an `L` — sharpen it until it is (a VC discharges or it does not).

### Group 4 — The actors and their disjoint `(U,L)` pairs
- **Who are the actors?** Start from the canonical cast; add a role only for a
  *new evidence base*. Two actors with identical `(U,L)` are one actor.
- **For each actor, what is its `(U,L)` pair?**
- **Disjointness check (C1):** do any two actors share a pair? Does any actor's
  `(U,L)` let it relieve *its own* constraint (e.g. the implementer also writes
  the tests, or the spec author reads the code)? If yes, the design is not yet
  compliant — split or rebarrier.
- **Catchability check (C2):** for each actor's characteristic blind spot, *which
  other actor catches it*? If none, you are missing a role or a pair.

### Group 5 — Context barriers (physical, not honorary)
- **What must each actor NOT see?** Most importantly: who must be denied the
  implementation? (The exerciser/verifier and the spec author must not see it.)
- **How is each barrier enforced in the delegation context?** Barriers live in
  *what is in the prompt* (fresh context; surface + acceptance lines only), not
  in an instruction to refrain. An actor with the internals in context will use
  them.

### Group 6 — Gates and "done"
- **Gate A (editorial):** the coordinator's *judgment* approval of the plan
  against `U` (amend / cut / sharpen — never a rubber stamp). No source edit
  from a `DRAFT`. What does Gate A check here?
- **Gate B (machine):** the executable acceptance check against `L` — positives
  pass; negatives fail *at the named site* violating the *named clause*; standing
  invariants green; nothing smuggled in (no added axioms/assumptions). What runs?
- **Gate C (coverage / no-blend / coherent-and-wrong):** each obligation clause
  maps to a passing check, and *the theorem proved is the property intended*
  (guard against vacuous/trivial passes and plane-blending). What is the map?
- **Done (C4):** "done" = which fixed set of machine-checked gates passes? No
  actor's self-report counts.

### Group 7 — The coherent-and-wrong failure specific to this problem
- **What would a plausible-but-wrong deliverable look like that passes the naive
  check?** (e.g. a contract so weak it is vacuously true; a proof of an adjacent
  weaker property; an abstract that over-claims the body.) Name it; it tells you
  what Gate C and the catchability pairing must target.

### Group 8 — Stabilizers / collapse modes to pre-empt
Walk the collapse modes and pick the ones this problem is prone to:
- **Self-judging** (an actor edits/authors its own acceptance) → forbidden moves
  + physical barriers.
- **Shared evidence** (two actors, one pair) → the (C1) disjointness audit.
- **Self-declared done** → gate-defined done.
- **Coherent-and-wrong / weakened clause** → Gate C + "where authority is
  authored, independence is the soundness argument" + "strictness has a safe
  direction" (stricter than `U` is legitimate; weaker is a bug).
- **Absorbed surprise** → route surprises to a gap document, never patch locally.
- **Rubber-stamp approval** → Gate A must amend/cut/sharpen.
- **Unpinned reality / unspecified base** → pilot first; transcribe the de facto
  base before extending it.
- **Unsequenced parallelism** → sequence by mechanism reuse; parallelize only
  across true independence.

---

## 2. How to draft the plan (template)

Once the slots are filled, emit the plan in this shape. Keep `ASSUMPTION:` and
`OPEN QUESTION:` markers where the human under-specified.

```
# SL Plan: <deliverable>

## 0. Deliverable & correctness
- Deliverable: ...
- "Correct" means (checkable): ...
- Terrain archetype: A / B / C (and why)
- Dominant coherent-and-wrong to guard: ...

## 1. Bounds
- Upper bound U: <the soft authority> — exists externally / authored upstream by <who>
- Lower bound L: <the executable oracle> — exists / must be built as item E-0

## 2. Actors and their disjoint (U,L) pairs
| Actor | Builds | U (above) | L (below) | Forbidden move | Must NOT see |
|-------|--------|-----------|-----------|----------------|--------------|
| coordinator | ... | binding spec sections | gate machine output | edit source; rubber-stamp | — |
| spec author | ... | <U_spec> | <L_spec> | read the implementation | the implementation |
| implementer | ... | <U_impl> | <L_impl> | touch acceptance evidence | acceptance evidence |
| exerciser/verifier | ... | <U_exer> | <L_exer> | read the implementation/diff | the implementation |
| probe (opt.) | ... | design claim | tool's actual behaviour | implement a fix | — |

Disjointness (C1): <no two pairs equal; intersection = correct deliverable>
Catchability (C2): <blind spot → who catches it> for each actor.

## 3. Gates
- Gate A (editorial): coordinator judges the plan against U — <checks>.
- Gate B (machine): <oracle runs; positives pass, negatives fail at named site;
  invariants green; no smuggled axioms/assumptions>.
- Gate C (coverage / no-blend): <clause→check map; the proved theorem IS the
  intended property; vacuity/blend guard>.

## 4. Loop steps (per item)
1. coordinator delegates item (U sections + barriers + acceptance lines)
2. implementer writes spec-N plan @ STATUS: DRAFT
3. Gate A → APPROVED (judge/amend/cut)
4. implementer implements + runs standing invariant
5. exerciser/verifier authors acceptance evidence from spec+surface only
6. Gate B (machine) → Gate C (coverage/no-blend)
7. item DONE → next; any divergence → gap-N doc → re-plan (N:=N+1)

## 5. Executable oracle setup
<how L is invoked; what "a verdict" is; what must be built first (pilot)>

## 6. Done criteria
<the fixed gate set; nothing self-reported>

## 7. Stabilizers engaged
<the chosen collapse-mode defenses from Group 8>

## 8. Execution order
<pilot/oracle first; sequence by mechanism reuse; parallel only across independence>
```

---

## 3. Worked example A — Frama-C C validation (single SL)

Request: *"Draft a plan to generate an SL validation of C code using Frama-C."*

**Deliverable:** C code proven to satisfy its requirement.
**Terrain:** A/B mix — the *requirement* is external (transcription) but the
**ACSL contracts** that make it checkable must be **authored upstream**
(authored authority), so author independence is load-bearing.
**Dominant coherent-and-wrong:** a **vacuously-true contract** — `ensures \true`,
an `assigns` clause so loose nothing is constrained, a postcondition implied by a
too-strong (unreachable) precondition. WP discharges, but the proved theorem is
not the property intended.

**Bounds**
- `U` = the requirement (plain English) **plus** a coding standard, made precise
  as ACSL contracts (requires/ensures/assigns/loop invariants).
- `L` = **Frama-C/WP proof-obligation discharge** — each VC discharges or it does
  not — **plus** test execution of the compiled code.

**Actors and disjoint (U,L) pairs**

| Actor | Builds | U (above) | L (below) | Forbidden move | Must NOT see |
|-------|--------|-----------|-----------|----------------|--------------|
| coordinator | approvals, sequencing, gate verdicts | the requirement + plan sections | gate output (WP logs, test logs) | edit C/ACSL; approve an unjudged plan | — |
| contract/spec author | the ACSL contracts from the requirement | the requirement + coding standard | expressibility: each clause dischargeable by *some* WP/test mechanism | propose or read the implementation | the C implementation |
| implementer | the C code satisfying the contracts | the ACSL contracts (strongest mandated claim) | WP discharge + standing test suite | weaken a contract/gate to land; touch acceptance properties | the acceptance/adversarial properties |
| exerciser/verifier | runs WP; authors adversarial properties from the spec only | the requirement's acceptance clauses + the documented surface | what actually discharges/proves when WP is run | read the implementation or any diff | the C implementation |
| probe (opt.) | minimal Frama-C experiments (does WP handle this construct?) | one design claim per probe | Frama-C's actual behaviour | implement a fix | — |

Disjointness (C1): the author holds the requirement (never the code); the
implementer holds the contracts (never the adversarial properties); the verifier
holds the spec + the runnable WP (never the code). No actor can relieve its own
constraint. Intersection = C that *both* discharges all VCs and meets adversarial
properties derived independently from the spec.
Catchability (C2): implementer's blind spot (writing C that games a weak
contract) is caught by the verifier's adversarial properties + the author's
clause coverage; the author's blind spot (a vacuous contract) is caught at
**Gate C** by the verifier (who proves the contract is non-trivial) and by the
adversarial properties that *should* fail against a vacuous spec.

**Gates**
- **Gate A (editorial):** coordinator approves the contract & plan — each
  requirement clause is typed and pre-bound to an ACSL obligation; the
  strongest-claim check; NOT-claims named. Amend/cut/sharpen, never rubber-stamp.
- **Gate B (machine):** all VCs **discharged** by WP; tests pass; **no axioms or
  `assumes`/`admit`/`lemma`-as-axiom smuggled in** to make a VC vanish; standing
  proof count (previously discharged VCs stay discharged — total additivity).
- **Gate C (coverage / no-blend / coherent-and-wrong):** every requirement clause
  maps to a *proven* contract clause, **and the proved theorem is the property
  intended** — i.e. guard against vacuous/trivial contracts: a non-vacuity check
  (the postcondition is reachable and constrains the output; the `assigns` set is
  tight; mutation of the implementation that violates the requirement is *caught*
  by some VC or adversarial property). Two planes — the *proof plane* (WP
  discharge) and the *test plane* (execution) — must never blend (a discharged VC
  never stands in for an untested runtime behaviour, and vice versa).

**Loop steps:** coordinator delegates a function/unit → contract author writes
ACSL @ DRAFT → Gate A → implementer writes C, runs WP locally → verifier runs WP
fresh + authors adversarial properties from the spec → Gate B → Gate C → DONE.
Divergence (a VC won't discharge, or a vacuity probe fires) → gap doc → re-plan.

**Executable oracle setup:** `frama-c -wp` over the unit; "a verdict" = the per-VC
discharge status; build the WP invocation + a determinism re-run convention as
the first item (pilot on the smallest function end-to-end before any sweep).

**Done:** **all proof obligations discharged** (no `Admitted`/axiom/`assumes`
shortcut), tests pass, Gate C coverage map complete, no vacuous contract.

**Stabilizers engaged:** guard against **vacuously-true contracts** (Gate C
non-vacuity check); **assigns/ensures gaming** (tight `assigns`; mutation check);
no smuggled axioms (Gate B); **strictness has a safe direction** (the C may be
stricter than the contract, never weaker); **author independence** (contract
author and verifier never see the code); **done is gate-defined**.

---

## 4. Worked example B — Nested SL (a monitor of a monitor)

Request: *"Draft a plan to generate an SL validating a bunch of C files. This SL
monitors another SL validating C code with Frama-C. The top-level SL starts with
leaf functions and coordinates contracts between compilation units."*

This is **two levels**. Use the `sl-monitoring-sl` meta-pattern (a loop
monitoring a loop): the top SL squeezes the **base SL's soft outputs** (the
contracts it infers or strengthens) against the **global spec**, from a disjoint
evidence base.

### Level 0 — the base SL (per compilation unit)
Exactly Example A, instantiated **once per compilation unit (CU)**. Each base SL
validates one CU with Frama-C/WP; its deliverable is that CU's functions proven
against their ACSL contracts. Its `U` = that CU's local contracts + the
requirement; its `L` = WP discharge + unit tests.

### Level 1 — the top-level SL (cross-CU contract coordination)
- **Deliverable:** a coherent set of **interface contracts across compilation
  units** such that every caller/callee pair is consistent and the whole program
  meets the global spec.
- **Strategy — bottom-up:** process **leaf functions first** (functions calling
  nothing un-contracted), then their callers. Propagate each callee's proven
  **`ensures` as the caller's `assumes`/`requires`**; reconcile interface
  contracts where a caller's expectation and a callee's guarantee disagree.
- **Upper bound `U_top`:** the **global / interface specification** (the
  cross-CU requirement: what the whole program must guarantee at its module
  boundaries).
- **Lower bound `L_top`:** the **base SLs' machine verdicts** — WP discharge
  *across* units (a callee's `ensures` actually proves; the caller's assumed
  `requires` is actually established at the call site) — **plus integration /
  link tests** of the linked binary.
- **It monitors the base SL (`sl-monitoring-sl`):** the base SL's *soft outputs*
  are the contracts it **infers or strengthens** while proving a CU. Those are
  learned, one-signal artifacts — they can be **coherent-and-wrong**: a contract
  the base loop strengthened to make *its own* VCs discharge may over-constrain a
  callee in a way the *global* spec forbids, or weaken an interface the global
  spec relies on. The top SL squeezes each such contract between `U_top` (the
  global spec — the contract must not contradict it) and `L_top` (cross-unit WP
  discharge + integration tests — the differential comparator), **from an
  evidence base the base SL's actors do not hold**.

**Two-level actor map**

| Level | Actor | Builds | U | L | Must NOT see |
|-------|-------|--------|---|---|--------------|
| base (per CU) | base coordinator / contract author / implementer / verifier | per-CU proofs (Example A) | local contracts + requirement | per-CU WP discharge + unit tests | (Example A barriers) |
| top | top coordinator | the bottom-up schedule; cross-CU gate verdicts; the contract-reconciliation ledger | global/interface spec | cross-unit WP verdicts + integration tests | the CU implementations |
| top | interface-spec author | the global interface contracts (what each boundary must guarantee) | the global requirement | expressibility across units | any CU implementation |
| top | **base-SL monitor** | per-contract verdicts on the base SLs' inferred/strengthened contracts | `U_top` (global spec the contract must not contradict) | `L_top` (cross-unit WP + integration tests, used as differential comparator) | the base SL's *rationale* for the contract; the CU code |

**The monitor's discipline (from `sl-monitoring-sl`):**
- It judges each inferred/strengthened contract **against `U_top` and `L_top`
  only** — never the base loop's account of *why* it inferred the contract, and
  it never edits the base SL's implementation. It emits a **verdict** (and a
  carve-out), never a silent fix.
- Verdicts: **PASS** (the contract agrees with the global spec, confirmed across
  units), **CARVE-OUT** (the contract over-reaches on some reachable cross-unit
  input → narrow it with an exception citing the global-spec clause it defers
  to), **REJECT/loud-fail** (the strengthened contract contradicts the global
  spec and cannot be reconciled → discard, gap doc, re-plan).
- Classify the contract by kind: a contract that **drops/ignores** a precondition
  the global spec needs is the high-risk *ignore-signal* kind → **trigger test**
  (perturb the dropped input across the link boundary; does a cross-unit VC or
  integration test move?) → carve-out. A contract that merely **follows** a
  callee guarantee the global spec sanctions is *defer-to-oracle* → **validity
  test** (does WP actually distinguish that case across units?) → usually PASS.

**How the top SL coordinates and audits the base SL**
1. Topo-sort the call graph; schedule **leaves first** (bottom-up).
2. For each function: run its **base SL** (Example A) to prove it against its
   contract. The base SL emits the proven `ensures` (and any contract it had to
   strengthen to discharge).
3. **Propagate:** the top coordinator installs each proven callee `ensures` as
   the caller's `assumes`, and records the binding in the reconciliation ledger.
4. **Audit (monitor):** before accepting a *strengthened* contract, the base-SL
   monitor squeezes it against `U_top`/`L_top` — does it hold across *all*
   callers (cross-unit WP), and does it contradict the global spec? PASS /
   CARVE-OUT / REJECT.
5. **Reconcile interfaces:** where a caller's required precondition and a callee's
   guarantee disagree, the divergence is a gap doc against the interface spec, not
   a silent edit; the interface-spec author re-authors the boundary contract,
   re-running affected base SLs.
6. **Top Gate C:** every global-spec clause maps to a cross-unit-proven interface
   contract; **no plane blends** — a *base* SL's local WP verdict never stands in
   for the *cross-unit* obligation or the integration test, and an inferred
   contract never silently substitutes for the global spec.

**Why two levels are disjoint (the soundness argument):** the base SLs hold
"what discharges within this CU"; the top SL holds "what the global spec mandates
across CUs" + "what discharges/links across CUs." These are **disjoint evidence
bases** — so a contract the base loop strengthened for *local* convenience that is
*globally* wrong is exactly the coherent-and-wrong the monitor is positioned to
catch, and the carve-out (the cross-unit exception) can only come from the actor
holding `U_top` and `L_top`, never from the base loop that produced the contract.

**Done (top level):** every CU's base SL DONE; every interface contract proven
consistent across all callers (cross-unit WP discharged); integration/link tests
pass; the reconciliation ledger complete; every base-SL-inferred contract has a
monitor verdict (PASS or carved); no global-spec clause unmapped.

---

## When invoked — operating procedure

1. Parse the request; mark each interview slot (Groups 1–8) KNOWN or MISSING.
2. If the request matches Example A or B, use it as the scaffold and ask only
   what diverges from it.
3. **ASK** the MISSING questions, grouped, with one-line rationale each. If the
   human wants the plan now, proceed with `ASSUMPTION:` markers.
4. **DRAFT** the plan in the §2 template.
5. Run the two checks before delivering: **(C1) disjointness** (no shared pair;
   no actor relieves its own constraint) and **(C2) catchability** (every blind
   spot has a catcher). Surface any unmet check as an `OPEN QUESTION:`.

Do not run git, commit, or edit files other than producing the plan in your
reply. This skill produces a *plan*, not the implementation.
