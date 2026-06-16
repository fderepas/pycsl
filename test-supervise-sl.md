# SL Plan: `test-supervise-sl` — supervise & monitor a fleet of `formal-test-sl` runs

A **monitor squeeze loop** (`sl-monitoring-sl`) that drives the base loop
`formal-test-sl` (see `formal-test-sl.md`). Given a **mission** in natural language
— e.g. *"analyze the `os` lib in `pure_lib`; write formal tests in `pure_lib_test`
for all system calls in `os`; specify the os lib thoroughly but disregard network
access"* — it decomposes the mission into a work-list, **launches one
`formal-test-sl` per work item as a sub-agent**, and squeezes each run's *returned
soft outputs* against the mission guidance, never trusting the base loop's
self-report. It accumulates audited knowledge into the skill
`config/skills/pycsl-monitoring/`, and files improvement ideas and bug reports
into `getting-better/` and `bugs-to-report/`.

Drafted with `sl-builder`; the monitoring discipline is `sl-monitoring-sl`.

---

## 0. Mission & "done"

- **Deliverable:** for a given mission, a **complete, scope-correct fleet** of
  `formal-test-sl` outcomes — every in-scope target either a fully-proven
  `pure_lib_test/formal_<name>.py` or a logged gap with a reason — plus an audited
  knowledge update and any filed suggestions/bugs.
- **"Correct" (checkable):**
  1. **Scope:** every in-scope target (per the guidance) has a `formal-test-sl`
     verdict; **no out-of-scope target** was tested.
  2. **Soundness:** every "DONE" the supervisor records is backed by a
     `formal-test-sl` machine verdict (`SUCCESS ∧ 0 non-Valid ∧ 0 \trusted`) that
     the supervisor **re-confirms is non-vacuous from its own disjoint base** — not
     the base loop's say-so.
  3. **Knowledge integrity:** every entry added to `config/skills/pycsl-monitoring/`
     passed **Gate S** (skill-consistency); every carve-out cites the guidance/spec
     clause it defers to.
- **Terrain:** **C (split planes) over B.** Two authorities: the **mission
  guidance** (what is in scope / how thorough — soft) and the **base-loop oracle**
  (what actually proved — hard). The dominant failure is **blending** them: letting
  "the base loop reported DONE" stand in for "in-scope AND proven non-vacuous", or
  letting a coverage *claim* stand in for a counted coverage *map*.
- **Dominant coherent-and-wrong to guard:**
  1. **Coverage over-claim** — "all syscalls done" while some are missing or only
     partially specified (scope blur).
  2. **Scope drift** — testing what the guidance excluded (e.g. network access when
     told to disregard it).
  3. **Rubber-stamped base verdict** — accepting a `formal-test-sl` "DONE" whose
     test is actually **vacuous** (the base loop's own Gate C rubber-stamped it).
  4. **Coherent-and-wrong skill** — a heuristic the base loop consolidated that is
     right on the common syscalls and silently wrong on a governed exception.

---

## Doctrine — EXTREME RIGOR (this loop is its bearer)

`test-supervise-sl` **carries and enforces the extreme-rigor doctrine** across every
base run it supervises. It is the authority that refuses any deliverable that buys a
green by lowering the bar. Two non-negotiable tenets, both refinements of the lower
bound `L` and the safe-direction stabilizer:

1. **Reduce the TCB (Trusted Computing Base).** "Fully proven" is not "SMT said
   Valid" — it is "Valid with the *smallest possible trusted base*."
   - **Zero `\trusted` is the target** for a formal test (the `formal-test-sl`
     deliverable already mandates `0 \trusted`).
   - Prefer **definitional, zero-TCB** constructions (an uninterpreted predicate with
     intro/elim that *derive from the body*) over any axiom.
   - Any axiom that must enter the TCB is **cross-validated in BOTH Rocq and Lean**
     (Rocq: "Closed under the global context"; Lean: `#print axioms` ⊆ {`propext`,
     `Quot.sound`}) and cited via `#@ proof rocq …` / `#@ proof lean …`. An
     un-cross-validated axiom is a **REJECT**.
   - The TCB **only ever shrinks**: a run that adds to it without cross-validation
     fails Gate B; the monitor records every trusted item as a residual to retire.

2. **Use a proof assistant when Why3/SMT fails — never weaken, never trust away.**
   When Alt-Ergo / Z3 return Unknown / Timeout / Out-of-memory on a goal, the safe
   direction is to prove it **harder**, not to relax it:
   - **Escalate the goal to Rocq or Lean**, discharge it in the kernel, and bind the
     result back via a cross-validated `#@ proof` lemma (the goal becomes
     SMT-*applied*; the heavy reasoning is done offline, the TCB still bounded by the
     dual-prover check).
   - **Forbidden under this doctrine:** weakening a contract to make SMT pass; adding
     `\trusted` to skip a goal; accepting an adjacent-weaker property. These are the
     *weakened-clause* and *trusted-escape-hatch* collapses.
   - "SMT can't do it" is therefore **never a stopping condition — it is a routing
     condition** (to the prover), recorded as such.

This doctrine sharpens the gates (§3): **Gate B** counts `\trusted` and rejects any
un-cross-validated axiom; **Gate C** rejects weaken-to-pass and adjacent-weaker;
**Gate S** rejects any consolidated skill that trades rigor for convenience. The
escalation heuristic itself — *"when SMT diverges (e.g. across a `#@ no_inline`
boundary), fold the fact into a definitional atom or discharge it in Rocq+Lean —
never `\trusted`"* — is recorded in `config/skills/pycsl-monitoring/` under Gate S.
(Background: the `csl-philosophy`, `rocq`, and `lean` skills.)

---

## 1. Bounds

- **Upper bound `U` (soft):** the **mission guidance** — the natural-language
  authority the supervisor must comply with: *which* targets are in scope, what to
  include/exclude ("disregard network access"), how thorough, and priority. `U`
  fixes the strongest coverage/scope claim the supervisor may make.
- **Lower bound `L` (hard, executable, the GROUND TRUTH):** the **`formal-test-sl`
  loop itself**. Its per-item verdict (`SUCCESS ∧ 0 non-Valid ∧ 0 \trusted`, and
  its non-vacuity seed result) is the runnable oracle the supervisor **cannot
  alter** — the supervisor cannot mark a target proven that `formal-test-sl` did
  not prove. Secondary `L`: the **os API surface** (`pure_lib/os/__init__.py`) —
  the ground truth of *what targets exist* (for the scope decomposition).

---

## 2. Actors and their disjoint `(U,L)` pairs

| Actor | Builds | `U` (above) | `L` (below) | Forbidden move | Must NOT see |
|-------|--------|-------------|-------------|----------------|--------------|
| **supervisor-coordinator** | the work-list, sequencing, gate verdicts, the **coverage ledger** | the mission | the base-loop verdicts + gate output | edit a test/module; mark a target DONE without a base verdict; **read a sub-agent's internal rationale** | base sub-agents' internals |
| **mission-scoper** | the in-scope / out-of-scope target set from the guidance | the mission guidance ("thorough os, disregard network") | the **actual API surface** (`os/__init__.py` — what syscalls exist) | invent a target; include excluded scope; drop an in-scope target | — |
| **skill-monitor** (Gate S) | per-skill verdicts on the base loop's returned soft outputs | the guidance + the module English spec | the base loop's proof oracle (used as differential comparator) | read the base loop's *rationale* for a skill; edit the base loop; emit a silent fix | the base loop's internals/rationale |
| **(observed) `formal-test-sl`** | one fully-proven formal test | (its own bounds — see `formal-test-sl.md`) | (its own PyCSL oracle) | (its own forbidden moves) | the module internals (its own barrier) |

The `formal-test-sl` instances are **not** monitor actors — they are the
**observed base loop**, launched one delegation level deeper (§5).

**Disjointness (C1):** the scoper holds *guidance + what exists* (never proves
tests); the skill-monitor holds *guidance + spec + the base verdict* (never authors
tests, never reads base rationale); the coordinator holds *the mission + gate
output* (never edits). Each base sub-agent holds *API + spec + property* and does
the proving — disjoint from the monitor, which never sees its internals.
**Intersection** = a fleet that is in-scope (scoper), proven (base oracle),
non-vacuous (skill-monitor's independent re-check), and coverage-complete
(coordinator's counted ledger).

**Catchability (C2):** the base loop's blind spot (a vacuous-but-DONE test, or an
over-general consolidated skill — it shares its own blind spot) is caught by the
**skill-monitor**, which judges from a *different* evidence base (the guidance +
the oracle), exactly as `sl-monitoring-sl` prescribes. The scoper's blind spot
(mis-scoping) is caught at **Gate A** and ultimately by the **human** (§9).

---

## 3. Gates

- **Gate A — editorial (mission decomposition, before any sub-agent).** The
  coordinator judges the **work-list + scope** against the guidance `U`:
  in-scope set complete? out-of-scope (network) excluded? each per-target property a
  genuine consequence? Must **amend / cut / sharpen**. No sub-agent is launched from
  a `DRAFT` work-list.
- **Gate B — machine (per item).** The `formal-test-sl` sub-agent's verdict **is**
  Gate B (it already ran PyCSL to `SUCCESS ∧ 0 non-Valid ∧ 0 \trusted` on the
  committed file). The supervisor **records** it; it cannot alter it. A
  `DEPENDENCY UNMET` / non-`SUCCESS` is logged as a **gap**, never a pass.
- **Gate C — coverage / no-blend / coherent-and-wrong.**
  1. **Coverage map:** every in-scope target maps to a base DONE **or** a logged
     gap; the map is *counted*, not asserted; no out-of-scope target appears.
  2. **No-blend:** "the base loop reported DONE" never stands in for "in-scope AND
     proven non-vacuous"; the supervisor **re-runs the non-vacuity check from its
     own disjoint base** (it does not trust the base loop's Gate C) — the
     stale-measurement / honorary-green lesson applied one level up.
- **Gate S — skill-consistency (`sl-monitoring-sl`, gates KNOWLEDGE).** Before any
  heuristic the base loop consolidated enters `config/skills/pycsl-monitoring/`, the
  skill-monitor squeezes it: classify (ignore-signal vs defer-to-oracle), run the
  matching check (trigger test / validity test), emit **PASS / CARVE-OUT / REJECT**.
  Carve-outs cite the guidance/spec clause; never silently keep an irreconcilable
  skill.

---

## 4. Loop mechanics (per mission)

1. **Receive the mission**; the **scoper** enumerates in-scope targets by reading
   the API surface (`L`) and applying the guidance (`U`) — e.g. all `os.*` syscalls
   minus the network-access set.
2. **Gate A** → coordinator amends/cuts/sharpens the work-list → `APPROVED`.
3. **For each work item**, launch a **`formal-test-sl` sub-agent** (§5) with exactly
   `(module, public API surface, english_property)` + the scope guidance; the
   sub-agent runs the full base loop and **returns its soft outputs** (the authored
   property + non-vacuity argument, the proof verdict, any consolidated skill).
   Sequence by mechanism reuse; parallelize only across targets sharing no contract.
4. **Gate B** record per item; **Gate C** re-check non-vacuity from the disjoint
   base; update the **coverage ledger**.
5. **Gate S** on each returned skill → PASS / CARVE-OUT / REJECT → on PASS/CARVE,
   write it (audited, traceable) into `config/skills/pycsl-monitoring/`.
6. **File outputs:** ergonomics ideas → `getting-better/`, candidate bugs →
   `bugs-to-report/` (naming §7).
7. **Mission DONE** iff the coverage ledger is complete (every in-scope target a
   DONE or a logged gap), every recorded DONE re-confirmed non-vacuous, every kept
   skill Gate-S-passed. Divergence (an unprovable target, a mis-scope) → gap doc →
   re-plan. The soft residual (is the scoping faithful to the guidance?) → human
   (§9).

---

## 5. Nesting — run each `formal-test-sl` as a sub-agent (load-bearing)

```
test-supervise-sl        (agent)      <- accumulates only the base loop's RETURNED soft outputs
  └─ formal-test-sl      (sub-agent)  <- the base loop's whole run lives & dies HERE
       └─ base actors    (sub-sub-agents: property author / driver author / verifier / probe)
```

Per `sl-monitoring-sl`, this nesting is the load-bearing mechanism on two axes that
are the same boundary:

- **It makes the barrier physical.** The skill-monitor's forbidden move is *reading
  the base loop's rationale*. Because the base loop runs in the sub-agent's context,
  its deliberation, oracle runs, and author reasoning **never cross back** — only
  the small soft outputs return. The monitor literally cannot judge against the
  rationale. **The sub-agent boundary IS the barrier.**
- **It keeps the supervisor's context bounded, so it scales.** Only one summary per
  base run accrues; the supervisor can drive a long fleet (all os syscalls) without
  its window overflowing. For very large missions, chunk and summarize-and-forget
  between batches.

---

## 6. Knowledge accumulation → `config/skills/pycsl-monitoring/`

All knowledge the supervisor gathers — proven formal-test patterns, the
coherent-and-wrong catalog for formal tests, the per-module coverage ledger — lives
in `config/skills/pycsl-monitoring/SKILL.md`. **Discipline:** an entry is added only
after **Gate S** (PASS or CARVE-OUT); every entry is **traceable** (which base run,
which clause, which inputs revealed a carve); a carve-out only ever makes a heuristic
*more* faithful to `U`, never licenses something `U` forbids. The base loop never
edits this store about itself — that would be self-judging; only the disjoint
skill-monitor writes here.

---

## 7. Outputs — `getting-better/` and `bugs-to-report/`

The agents file two kinds of artifact (one concern per file):

- **`getting-better/`** — *.md proposing a PyCSL/tooling feature that would make
  writing or proving formal tests easier (an ergonomic gap surfaced during a run).
- **`bugs-to-report/`** — *.md describing a candidate PyCSL bug (emitter/prover/
  gate) encountered during a run, with a minimal repro and a `STATUS:`
  (`CONFIRMED` / `UNCONFIRMED`). Per the loud-fail discipline, never file an
  unconfirmed bug as confirmed.

**Filename format (both):** `YYYYMMDD-hhmm-simple-name.md`
(e.g. `20260616-1547-handle-reference.md`).

---

## 8. Stabilizers engaged

| Collapse mode | Blocked by |
|---|---|
| Rubber-stamped base verdict (honorary green) | Gate C re-runs the non-vacuity check from the disjoint base; never trusts the base loop's self-report |
| Self-declared done | done = counted coverage ledger + machine base verdicts, never a "reported success" |
| Scope drift | the scoper's `U`=guidance / `L`=API-surface squeeze + Gate A |
| Coverage over-claim | coverage map is *counted* (each in-scope target ↔ a verdict), not asserted |
| Self-judged knowledge | only the disjoint skill-monitor writes `config/skills/pycsl-monitoring/`; never the base loop about itself |
| Coherent-and-wrong skill | Gate S (trigger/validity test) before any skill is kept |
| Honorary barrier | base loops run as **sub-agents**; the monitor sees only returned soft outputs |
| Absorbed surprise | an unprovable target / mis-scope → gap doc → re-plan; never a silent local fix |
| Scope blur | honest residual ledger; out-of-scope exclusions named explicitly |
| Trusted escape hatch | the **extreme-rigor doctrine**: zero `\trusted` target; any axiom cross-validated Rocq+Lean; TCB only shrinks |
| Weaken-to-pass / "SMT can't, so stop" | the **extreme-rigor doctrine**: SMT failure routes to a proof assistant; weakening or trusting-away is a Gate-C/Gate-S REJECT |

---

## 9. The residual (route to a disjoint base = the human)

The supervisor's own **soft-vs-soft** judgment — *"is my scoping a faithful reading
of the mission guidance (did I correctly interpret 'thorough os, disregard
network')?"* — has **no executable lower bound** and cannot be self-certified
(an internal audit shares the supervisor's blind spot). It is routed to the
**human** (the standing disjoint base; checks later), with the work-list, the
exclusions, and the coverage ledger emitted legibly so the human can refute a
mis-scope. The supervisor must **never** mark a mission DONE on its own judgment of
scope faithfulness.

---

## Worked example — the stated mission

> *"Analyze the `os` lib in `pure_lib`; write formal tests in `pure_lib_test` for
> all system calls in `os`; specify the os lib thoroughly but disregard network
> access."*

1. **Scoper:** read `pure_lib/os/__init__.py` (and `UnixInodeFileSystem.py`),
   enumerate the public syscalls (`open`, `read`, `write`, `pread`, `close`,
   `mkdir`, `rmdir`, `unlink`, `rename`, `link`, `symlink`, `readlink`, `stat`,
   `lstat`, `fstat`, `dup`, `lseek`, `chmod`, `truncate`, …). Apply the guidance:
   **exclude** any network-access surface; keep the filesystem syscalls. Output the
   in-scope work-list (one item per syscall, each with a *consequence* property,
   e.g. `mkdir`→`stat` sees it; `write`→`pread` returns the bytes).
2. **Gate A:** amend (is `readlink` content in scope? note `rename` is the known
   hard one; mark NOT-claims like "no network").
3. **Per item:** launch a `formal-test-sl` sub-agent → it authors + proves
   `pure_lib_test/formal_os_<syscall>.py` and returns its soft outputs.
4. **Gate C:** for each returned DONE, re-confirm non-vacuity from the disjoint base
   (the test would FAIL if the syscall were broken); update the coverage ledger.
5. **Gate S:** the base loop will likely consolidate skills (e.g. *"cross a
   `#@ no_inline` boundary with a folded uninterpreted atom, never a bare `∀i`"*) —
   trigger-test each, then write the survivors into `config/skills/pycsl-monitoring/`.
6. File any ergonomics gaps (e.g. an API-surface lister) into `getting-better/` and
   any candidate tool bugs into `bugs-to-report/`.
7. **DONE** when every in-scope syscall has a proven test or a logged gap (e.g.
   `rename` may be a logged hard residual), the coverage ledger is complete, and no
   network surface was touched. Scope-faithfulness → human.

---

## Decisions (approved 2026-06-16)

These were drafted as assumptions and are now **approved** — they are settled
design, not tentative:

- **DECIDED — output locations.** `getting-better/` and `bugs-to-report/` are
  **repo-root directories** (the literal paths as given). Not relocated under
  `config/skills/pycsl-monitoring/`.
- **DECIDED — what "system call" means.** A *system call* is a **public `os.*` API
  symbol in `pure_lib/os/__init__.py`**. The disjoint scope check reads that file as
  the **ground truth of what exists**; the in-scope work-list is "the symbols it
  declares, minus the guidance's exclusions."
- **DECIDED — sub-agent nesting + sanctioned fallback.** True sub-agent nesting
  (`test-supervise-sl` → `formal-test-sl` → actors, §5) is the design. **Where the
  harness lacks real nested delegation, the sanctioned fallback** is: run each base
  loop in a **fresh, isolated delegation** and **discard its rationale on return**,
  keeping only the soft outputs — an honest approximation of the physical barrier.
  When the fallback is used, record the disjointness as **partial** (the barrier is
  procedural rather than structural), never as full — so the bookkeeping stays
  honest about which barrier was actually in force.
