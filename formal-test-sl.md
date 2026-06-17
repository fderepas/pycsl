# SL Plan: `formal-test-sl` — create and fully prove a PyCSL formal test

A reusable Squeeze Loop (SL) whose deliverable is **one fully-proven PyCSL formal
test** for a given `pure_lib/` module + property. Drafted with the `sl-builder`
skill. It is the **base loop**: a future monitor `test-supervise-sl`
(`sl-monitoring-sl`) will launch instances of this loop as sub-agents and squeeze
their *returned soft outputs* (§9). Do not design `test-supervise-sl` here.

Generic over its input `(module, public_api_surface, english_property)`; instantiate
once per formal test. Output file: `pure_lib_test/formal_<name>.py`.

---

## 0. Deliverable & correctness

- **Deliverable:** a `pure_lib_test/formal_<name>.py` driver that states an
  end-to-end property of a module's **public API** over **symbolic** inputs as a
  `#@ ensures`, and that PyCSL proves.
- **"Correct" (checkable):** PyCSL run on the committed file reports
  `Verification SUCCESS`, **every VC Valid, 0 non-Valid (incl. Timeout / Unknown /
  Out of memory), and ZERO `\trusted`** — AND the test is a genuine **consequence**
  (setup → operate → observe), AND it **calls the public API only** (never simulates
  the op on the data structure, never inlines internals).
- **Terrain archetype:** **A + B mix.** The property's authority is the module's
  English / POSIX-style spec (transcription, **A**); the *consequence framing* of
  that property must be **authored** from the spec by an actor who never sees the
  implementation (authored authority, **B** — author independence is load-bearing).
  A third **no-blend (C)** plane separates emission/typecheck, proof, and
  non-vacuity (§3, Gate C).
- **Dominant coherent-and-wrong to guard (the vacuous test):**
  1. **Self-return assertion** — calls the op and asserts the op's *own* return
     code (`#@ ensures \result == 0 or \result == 1`). Holds even if every op
     fails. (`[[feedback-formal-test-consequence]]`.)
  2. **Simulation** — re-implements the op on the data structure / inlines
     internals instead of calling the public API. (`[[feedback-test-calls-api]]`.)
  3. **Adjacent-weaker** — proves the byte-**count** round-trip while claiming the
     byte-**value** round-trip (the `formal_0008` `back == c` int-vs-array trap).
  4. **Plane blend** — emission/typecheck success standing in for proof success;
     a `--no-proof` green reported as "proven".

---

## 1. Bounds

- **Upper bound `U` (soft):** the module's English/POSIX spec for the operation +
  its **public API contracts** (the `val` contracts exposed in
  `pure_lib/<m>/__init__.py`) + the methodology rules (a test is a *consequence*;
  a test *calls the API*; honest NOT-claims). `U` fixes the strongest property the
  test may assert.
- **Lower bound `L` (hard, executable):**
  `PYTHONHASHSEED=0 PYTHONPATH=src/pycsl .venv/bin/python -m pycsl pure_lib_test/formal_<name>.py`
  → verdict = `SUCCESS ∧ 0 non-Valid ∧ 0 \trusted`. Sub-oracles:
  `--no-proof` (typecheck plane); a **non-vacuity re-run** with a seeded mutation
  that *must* flip the test to FAIL (the coherent-and-wrong calibrator).
  `L` exists today — no build needed.

---

## 2. Actors and their disjoint `(U,L)` pairs

| Actor | Builds | `U` (above) | `L` (below) | Forbidden move | Must NOT see |
|-------|--------|-------------|-------------|----------------|--------------|
| **coordinator** | approvals, sequencing, gate verdicts, gap docs | the task `(module, API, english_property)` + methodology rules | gate machine output (PyCSL verdicts) | edit the driver/contracts; approve an unjudged property | — |
| **property author** | the property spec: symbolic-input `requires` (bounds), the `ensures` consequence, NOT-claims, **the non-vacuity argument** (which observable consequence; why it is *not* the op's own return code) | the module's English/POSIX spec + the documented API surface | **expressibility**: every clause dischargeable by *some* PyCSL mechanism, AND the property is a setup→operate→observe consequence | propose/read the implementation; write the driver | the module implementation internals |
| **driver author** (the test-agent) | `formal_<name>.py`: symbolic inputs, the setup→operate→observe **public-API** call sequence, the `#@` contracts realizing the approved property | the **approved property** (strongest claim) + the **public API surface only** | PyCSL **emits + typechecks**; the driver calls only the public API | simulate the op on the data structure / inline internals; weaken the property to land; touch the verifier's seeds | **the module internals** (gets ONLY API + spec — `[[feedback-test-calls-api]]`) |
| **verifier / exerciser** | runs PyCSL fresh; the **non-vacuity seed**; the API-only audit | the property's acceptance clauses + the documented surface | what actually proves when PyCSL runs **on the committed file** | read the implementation; edit the driver/contracts; declare done from an intermediate/stale run | the module internals; the author's rationale |
| **probe** (opt.) | one minimal PyCSL experiment, one recorded verdict (does the API expose enough to *state* the property? does clause X discharge in isolation?) | one design claim per probe | PyCSL's actual behaviour | implement the test or a fix | — |

**Disjointness (C1):** property author holds the *English spec* (never internals,
never the driver); driver author holds the *approved property + API* (never
internals — the physical barrier — never the seeds); verifier holds the
*acceptance clauses + the runnable PyCSL* (never internals, never the driver). No
actor can relieve its own bound. **Intersection** = a formal test that (a) PyCSL
proves 0/0 with no `\trusted`, (b) the verifier independently confirms is a
non-vacuous API-level consequence, and (c) asserts a property faithful to the
English spec — where (c)'s *soft-vs-soft faithfulness* is the residual routed up to
`test-supervise-sl` (§8, §9).

**Catchability (C2):** driver author's blind spot (gaming a weak property /
simulating) → caught by the verifier's non-vacuity seed + API-only audit, and by
the property author's clause coverage. Property author's blind spot (a vacuous /
adjacent property) → caught at **Gate C** (non-vacuity calibration) and ultimately
by the **monitor** (`test-supervise-sl`), since "is this property faithful to the
spec?" has no internal executable refuter.

**Barriers are physical, not honorary (C3):** the driver author's delegation
context contains the **public API + the spec + the approved property and nothing
else** — the module source is *absent*, not "off-limits". An author who can't see
the internals *cannot* simulate them — the barrier makes the dominant
coherent-and-wrong (simulation) structurally impossible rather than discouraged.

---

## 3. Gates

- **Gate A — editorial (judgment).** Coordinator judges the **authored property
  before any driver code**: is it a genuine **consequence** (setup→operate→observe),
  not the op's own return code? Are the NOT-claims named? Is it the *strongest
  faithful* claim (not adjacent-weaker)? Must **amend / cut / sharpen** — a rubber
  stamp makes `U` fictional. No driver is written from a `DRAFT` property. *The
  deeper soft-vs-soft "is this property truly faithful to the English spec, vs a
  plausible adjacent one" is emitted as a returned soft output for the monitor
  (§9) — Gate A here enforces the mechanizable part (consequence-shape,
  NOT-claims, strongest-claim).*
- **Gate B — machine (the hard truth).** PyCSL **emits + typechecks**; **all VCs
  Valid; 0 non-Valid** (scan EVERY status incl. `Out of memory` —
  `[[os-gate-does-not-verify-method-bodies]]`); **0 `\trusted`**. Run
  `PYTHONHASHSEED=0` **on the committed file** (a determinism re-run), and confirm
  the module's own gate (`__init__` / body) **stays green** — the test is additive
  and "only ever improves". **Never re-report an intermediate count** (the
  stale-measurement collapse caught this session: a green claim taken from an
  intermediate run while the committed artifact was red).
- **Gate C — coverage / no-blend / coherent-and-wrong.**
  1. **Clause map:** each clause of the English property maps to a specific
     `#@ ensures` that PyCSL proved.
  2. **Non-vacuity (calibration):** the driver **calls the public API** (audited,
     no internals), AND a **seeded mutation that breaks the op's consequence is
     caught** — re-run with a deliberately-wrong assertion / a perturbed expected
     value and confirm the test flips to **FAIL**. *A formal test that would still
     pass with the op broken has proven nothing* — a missed seed **voids the run**.
  3. **No-blend:** a `--no-proof` (emission) green never stands in for a proof
     green; a proof of an adjacent weaker property never stands in for the intended
     one.

---

## 4. Loop steps (per formal test)

1. **coordinator** receives `(module, API surface, english_property)`; terrain
   check; delegates with barriers (driver author gets API + spec only).
2. **property author** writes the property spec `@ STATUS: DRAFT` — symbolic-input
   `requires` (bounds), the `ensures` consequence, NOT-claims, the non-vacuity
   argument.
3. **Gate A** → coordinator amends/cuts/sharpens → `APPROVED`. (Faithfulness
   residual recorded for the monitor.)
4. **probe** (if needed): does the API expose enough to *state* the property
   (e.g. is there a content-returning read before claiming a content round-trip)?
   does each clause discharge in isolation? Pin reality before the full driver.
5. **driver author** (barriered) writes `pure_lib_test/formal_<name>.py` — symbolic
   inputs, the setup→operate→observe **public-API** sequence, the `#@` contracts.
6. **Gate B** (machine): emit+typecheck; all VCs Valid; 0 non-Valid; 0 `\trusted`;
   committed-file re-run; module gate still green.
7. **verifier** runs PyCSL fresh; runs the **non-vacuity seed** (must FAIL);
   audits API-only.
8. **Gate C** (clause map + non-vacuity caught + no-blend).
9. **DONE** iff Gates A+B+C pass, witnessed by independently-authored evidence.
   Any divergence → **gap-N doc** → re-plan (`N := N+1`). A clause that won't
   discharge usually means a missing **leaf** VALUE contract — route **bottom-up**
   (`[[feedback-leaf-first]]`), never weaken the test or simulate.

---

## 5. Executable oracle setup (`L`)

- **Proof plane:** `PYTHONHASHSEED=0 PYTHONPATH=src/pycsl .venv/bin/python -m pycsl pure_lib_test/formal_<name>.py`;
  verdict = `SUCCESS ∧ V>0 ∧ nonV==0 ∧ \trusted==0`.
- **Typecheck plane:** same with `--no-proof` (must not be reported as proof).
- **Non-vacuity oracle:** re-run with a seeded falsification (wrong expected value
  / perturbed input); the run **must** flip to FAIL. (Cf. `verify/perturbation.py`
  if present.)
- **Standing invariant:** the module's `__init__`/body gate stays green after the
  test is added (additivity).
- **Pin reality first:** confirm the API symbols exist in `pure_lib/<m>/__init__.py`
  before authoring the property (probe).

---

## 6. Done criteria

`DONE` ⇔ **Gate A** (property approved: genuine consequence, NOT-claims, strongest
faithful claim) **∧ Gate B** (PyCSL `SUCCESS`, 0 non-Valid, 0 `\trusted`,
committed-file determinism re-run, module gate green) **∧ Gate C** (clause map
complete, non-vacuity seed caught, no plane blend). No actor's self-report counts.
The **soft-vs-soft faithfulness** residual is *not* self-certified — it is routed
to `test-supervise-sl` (human checks later).

---

## 7. Stabilizers engaged

| Collapse mode | Blocked by |
|---|---|
| Self-judging | physical barrier — driver author never sees internals; verifier never edits the driver |
| Self-declared done | Gate-defined done; **committed-file re-run** (the stale-measurement lesson) |
| Coherent-and-wrong (vacuous / adjacent) | Gate C non-vacuity seed + author independence (property & driver authors never saw internals) |
| Simulation | the physical barrier makes it impossible (internals absent from context) |
| Weakened clause | strictness has a safe direction — the test may assert a **stronger** property, never weaker; weakening to land is a bug → gap doc |
| Absorbed surprise | a non-discharging clause → **gap doc**, fix the missing **leaf** contract bottom-up; never silently simulate or weaken |
| Unpinned reality | probe: confirm the API exposes enough to state the property before writing the driver |
| Plane blend | Gate C no-blend: emission ≠ proof; adjacent-weaker ≠ intended |
| Regression | standing invariant: module gate stays green; determinism re-run |
| Scope blur | honest NOT-claims + residual ledger in the driver docstring (e.g. "proves on-fd round-trip, NOT reopen-by-name") |

---

## 8. Execution order

Pin the oracle + API existence first (probe); then property → Gate A → driver →
Gate B → verify → Gate C. Sequence formal tests by **mechanism reuse** (a content
round-trip rides the folded-atom machinery a prior one hardened); parallelize only
across modules that share **no contract and no deliverable**.

---

## 9. Interface to the supervising loop (`test-supervise-sl`, deferred)

`formal-test-sl` is the **base loop**; `test-supervise-sl` is its **monitor**
(`sl-monitoring-sl`). Per that skill's load-bearing rule, the monitor **launches
each `formal-test-sl` as a sub-agent one level deeper** — so this loop's internal
rationale (its deliberation, oracle runs, author reasoning) stays in its own
context and **never crosses back**; only the **returned soft outputs** below
surface to the monitor, which makes the author-separation barrier physical and
keeps the monitor's context bounded.

**Returned soft outputs (what this loop must emit for the monitor to squeeze):**
- the **authored property** (English + the `#@` contract) and its **non-vacuity
  argument** — the monitor squeezes faithfulness against `U` (the English spec) and
  `L` (PyCSL) from a disjoint base;
- the **proof verdict** (V / nonV / `\trusted` count, on the committed file);
- any **consolidated skill / heuristic** this loop learned (e.g. "for content
  round-trips, cross the `#@ no_inline` boundary with a folded uninterpreted atom,
  never a bare `∀i`") — Gate S in the monitor will trigger-test it and PASS /
  CARVE-OUT / REJECT.

**The residual this loop cannot self-certify:** "is the property a faithful,
non-vacuous reading of the English spec, rather than a plausible adjacent one?" has
no internal executable refuter — it is routed to `test-supervise-sl` (and, behind
it, the human). This loop must therefore emit the property and its justification
**legibly and honestly**, and never mark a test `DONE` on its own soft judgment of
faithfulness.

---

## Open questions / assumptions

- `ASSUMPTION:` formal tests target `pure_lib_test/formal_<name>.py` (the unified
  topical scheme), **not** the `test-suite/corpus/pycsl-reference/` corpus (a
  separate, intentional scheme for annotation-feature tests).
- `ASSUMPTION:` the non-vacuity seed is realized as a transient
  wrong-assertion / perturbed-input re-run; if a reusable `verify/perturbation.py`
  primitive is wanted, that is a follow-up item.
- `OPEN QUESTION:` `test-supervise-sl` (the monitor: Gate S over returned skills,
  cross-provider vs human Gate-A authority) is **deferred** by request.
