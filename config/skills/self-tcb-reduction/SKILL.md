---
name: self-tcb-reduction
description: >-
  Runs the self-tcb-reduction Squeeze Loop (SL): converts the PyCSL self-annotation
  mirror's ~1290 `\trusted` stubs into verified body-faithful methods, one at a time,
  tier by tier (T1 Module-6 emitter first), driving the trusted core down to its
  irreducible floor (recursion leaves + D2 axioms). Every conversion is held between a
  soft upper bound U (the live emitter body + a type-safety+frame contract shape + the
  item-3 ceiling doctrine) and three disjoint hard lower-bound oracle planes L
  (mirror-sync fidelity, Why3 proof, byte-diff-0 corpus inertness). Use when the user
  says: "run the tcb reduction loop", "squeeze the trusted stubs", "convert the next
  \trusted stub", "reduce the self-annotation TCB", "un-trust the expression handlers",
  or asks to execute self-tcb-reduction.md. Companion plan: self-tcb-reduction.md;
  machine-readable config: self-tcb-reduction.json (same directory).
---

# self-tcb-reduction — the TCB-reduction Squeeze Loop

This skill **executes** the campaign in `self-tcb-reduction.md`: it shrinks the self-annotation
mirror's trusted core by converting `\trusted` stubs to verified bodies, run as a disjoint-actor
Squeeze Loop so the dominant *coherent-and-wrong* failures cannot pass silently. It is an
operating procedure, not a plan-drafter — read `config/skills/sl-internal` for the SL theory and
`self-tcb-reduction.md` for the tiering/floor.

## 0. Deliverable & correctness

- **Deliverable:** the mirror (`src/self-annotate/src/`) with its `\trusted`-stub count driven to
  the irreducible floor — every `.py` stub either a **verified body** or **floor-audited** into
  F1/F2/F3 with a recorded reason.
- **"Correct" (checkable), per converted stub:** its mirror body is **verbatim-identical** to the
  live emitter method (fidelity), it **discharges** its `assigns`-framed contract under Why3
  (type-safety), it is **byte-diff 0** across the 627-corpus (corpus inertness), the total
  `\trusted` `wc -l` **strictly decreased**, and no axiom was smuggled in.
- **Terrain: A (transcription) + C (split planes).** The live emitter is the transcription source;
  "correct" splits across three disjoint oracle planes that must never blend.
- **Dominant coherent-and-wrong to guard:** (1) **mirror drift** — a stub that "verifies" a stale
  copy; (2) **corpus perturbation** — a recognizer that quietly changes real-program output;
  (3) **reclassification dodge** — mislabelling a convertible stub as "irreducible floor" to skip
  the work; (4) **fake-axiom / weakened frame** — a stub "verified" by an added axiom or a loose
  `assigns`.

## 1. Bounds

- **Upper bound `U`** (soft, transcription authority): the **live** emitter method in
  `src/pycsl/…` (the body to transcribe verbatim) **+** the fixed contract shape
  `#@ requires True / ensures True / assigns <tight-frame>` (type-safety + frame — **never**
  value-faithful `ensures \result == <string>`, **never** vacuous) **+** the item-3 ceiling
  doctrine (`remaining-trust.md`, `item34.md §1`) that bounds what may be re-sited to the floor.
- **Lower bound `L`** (three disjoint executable planes, ALL required):
  - **Fidelity:** `bin/check-self-annotate-sync.sh` ∧ `bin/self-annotate-mirror-check.sh`
    (the mirror body == the live body, verbatim modulo `#@`).
  - **Type-safety:** `python3 src/pycsl/pycsl.py <mirror> --import-path src/pycsl` — Why3 proof
    discharges; `proof_axiom_allowlist` unchanged (no smuggled axiom).
  - **Corpus inertness:** `PYTHONHASHSEED=0 bin/byte-diff-sweep.sh` + `diff -rq` vs a clean
    baseline == 0; and `bin/run-self-annotation-suite.sh` has no new failure; and the `\trusted`
    `wc -l` strictly shrank.

## 2. Actors and their disjoint (U,L) pairs

| Actor | Builds | U (above) | L (below) | Forbidden move | Must NOT see |
|-------|--------|-----------|-----------|----------------|--------------|
| **coordinator** | tier work-list, per-stub delegation, gate verdicts, the shrinking-count ledger | `self-tcb-reduction.md` (tier order + floor denylist) | the gate machine outputs | edit mirror/emitter; rubber-stamp a conversion | — |
| **converter** (implementer) | the verbatim mirror body + the `assigns`-framed `#@` + any `@mutable_state`-gated recognizer in the LIVE emitter | the live emitter method + the fixed contract shape | Why3 **type-check** discharge (`--no-proof`) locally | weaken/vacuate a contract; add an axiom; touch the corpus baseline or the floor-audit | the byte-diff baseline; the floor-auditor's reasoning |
| **verifier** (exerciser) | runs the three L planes **fresh from the surface only**; authors the non-vacuity + non-drift checks | the plan's gate battery + the contract shape | the actual oracle verdicts (sync exit, `diff -rq`, proof, `wc -l`, suite) | read the converter's recognizer rationale; edit mirror/emitter | the converter's diffs (surface + gate results only) |
| **floor-auditor** (monitor) | a PASS/REJECT verdict on every **re-siting** of a stub to F1/F3 | the item-3 ceiling doctrine (Gödel-2/Löb) | the floor register + a differential: did a genuine conversion attempt actually fail? | reclassify a stub itself; implement a fix | the converter's *convenience* motive |
| **triage probe** (opt., parallel) | one recorded classification per stub: trivial-leaf / needs-recognizer / hard-architectural / floor | the plan's tier definitions | the stub's actual shape (does `--no-proof` pass as-is?) | implement any conversion | — |

- **Disjointness (C1):** converter holds the live emitter + type-check (never the corpus baseline
  or the ceiling doctrine); verifier holds the acceptance oracles (never the code rationale);
  floor-auditor holds the ceiling doctrine (never the convenience motive). No actor can relieve its
  own constraint. **Intersection = a stub that is verbatim-faithful ∧ type-safe ∧ corpus-inert ∧
  (if re-sited) genuinely irreducible.**
- **Catchability (C2):** converter's *mirror drift / corpus perturbation* → caught by verifier
  (sync + byte-diff 0); converter's *vacuous/weak contract* → caught by verifier's non-vacuity +
  the fixed shape; converter's *dodge-by-mislabelling* → caught by floor-auditor; coordinator's
  *accept-unjudged* → gate-defined done.

## 3. Gates

- **Gate A (editorial):** coordinator judges the per-stub delegation — right tier, **not** on the
  floor denylist, contract shape correct (type-safety + frame; not value-faithful; not vacuous).
  Amend/cut/sharpen; never rubber-stamp. No mirror edit from a `DRAFT`.
- **Gate B (machine):** all three L planes pass — fidelity (both sync gates) ∧ type-safety (Why3
  discharge, allowlist unchanged) ∧ corpus inertness (byte-diff 0 ∧ suite no-new-fail ∧ `wc -l`
  strictly decreased). Nothing smuggled (no added axiom/`assumes`).
- **Gate C (coverage / no-blend / coherent-and-wrong):** the **three planes never blend** — a Why3
  discharge never stands in for byte-diff 0, and neither stands in for fidelity; **non-vacuity**
  (the `assigns` frame is tight; the body is the real transcription, not a stub); every **re-sited**
  stub carries a **floor-auditor PASS**. The count-map: every touched stub is either `VERIFIED` or
  `FLOOR:{F1|F3}+reason` in the ledger — none left `TRUSTED-unclassified`.

## 4. Loop steps (per stub)

1. **coordinator** picks the next stub from the current tier's work-list (skip the floor denylist),
   delegates with the surface only (live method body + contract shape + barriers).
2. **converter** ports the live body **verbatim** into the mirror, adds the `#@` contract, adds any
   `@mutable_state`-gated recognizer the emitter needs, runs `--no-proof` locally @ `STATUS: DRAFT`.
3. **Gate A** → APPROVED (coordinator judges tier/denylist/contract-shape).
4. **converter** removes the `\trusted` marker, commits the increment.
5. **verifier** runs the three L planes **fresh** (sync, proof, byte-diff 0, suite, count).
6. **Gate B** (machine) → **Gate C** (no-blend + non-vacuity + floor-audit if re-sited).
7. stub **DONE** → next. **Escalation:** a per-stub **attempt budget** (default 3 recognizer
   passes); on exceed → **revert** that stub, hand to **floor-auditor** to triage
   *hard-architectural* (flag for a focused human/high-reasoning pass — e.g. the `match`-class) vs
   *genuine floor* (re-site with reason). Any **regression** a gate catches → revert → **gap doc** →
   re-plan.

## 5. Executable oracle setup

Pin the byte-diff baseline once (a clean-tree corpus sweep) as **work item E-0**; every stub diffs
against it. "A verdict" = the conjunction of §1's three L planes plus the strictly-decreasing
`\trusted` count:

```bash
# E-0 (once): clean baseline — stash local edits, sweep df55a984-equivalent HEAD, restore.
# Per stub (converter, local): fast type-check
python3 src/pycsl/pycsl.py <mirror-file> --import-path src/pycsl --no-proof
# Per stub (verifier, fresh): the three planes + count
bash bin/check-self-annotate-sync.sh && bash bin/self-annotate-mirror-check.sh          # fidelity
python3 src/pycsl/pycsl.py <mirror-file> --import-path src/pycsl                          # type-safety (proof)
PYTHONHASHSEED=0 bash bin/byte-diff-sweep.sh /tmp/after && diff -rq <baseline> /tmp/after # corpus inertness
bash bin/run-self-annotation-suite.sh                                                    # no new failure
find src/self-annotate/src -name '*.py' -exec grep -h '\trusted' {} \; | wc -l           # must shrink
```

Amortize the slow planes: type-check per stub; batch proof + byte-diff per **file** (not per stub).

## 6. Done criteria (gate-defined, never self-declared)

Every mirror `.py` stub is `VERIFIED` or `FLOOR:{F1|F3}+reason`; the `\trusted` `wc -l` is at the
enumerated floor (F1 leaves + F3 boundaries; F2 = the 37 `.mlw` axioms); `check-self-annotate-sync.sh`
∧ `self-annotate-mirror-check.sh` ∧ `run-self-annotation-suite.sh` all green; byte-diff 0 held
throughout; `proof_axiom_allowlist` unchanged.

## 7. Stabilizers engaged (collapse-mode defenses)

- **Vacuous/weak contract** → Gate C non-vacuity (tight `assigns`; real body) + fixed contract shape.
- **Mirror drift** (self-judging on a stale copy) → the physical fidelity gate; converter never
  owns the sync verdict.
- **Corpus perturbation** → byte-diff 0 on every stub (physical, converter can't relieve it).
- **Smuggled axiom** → `proof_axiom_allowlist` diff in Gate B.
- **Reclassification dodge** → independent floor-auditor with the ceiling doctrine as its `U`.
- **Plane-blending** → Gate C requires all three planes; none substitutes for another.
- **Self-declared done** → gate-defined done; **unsequenced parallelism** → sequential per-file
  execution (shared emitter recognizers ⇒ conflicts), parallel only for the one-shot triage probe.
- **Escalate-not-thrash** → per-stub attempt budget; the hard tail is flagged, not ground on.

## 8. Execution order

E-0 baseline first → **T1.a** (24 `_handle_*_expr`, read-only first: `var`/`attribute`/`field_get`,
broadest last: `call`/`fstring`) → **T1.b** (Module-6 helpers, dependency order) → **T2**
(`core_ir_semantic`, spike one method to fix the analyzer-invariant contract class, then batch) →
**T3** (front-end, demand-gated, leaf-first) → **T4** (re-site to F3, convert only on demand).
Parallelize only the triage probe; everything else serializes by shared-recognizer reuse.
