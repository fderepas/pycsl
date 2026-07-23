---
name: self-tcb-reduction
description: >-
  Runs the self-tcb-reduction Squeeze Loop (SL): converts the PyCSL self-annotation
  mirror's `\trusted` stubs into verified body-faithful methods, held between a soft upper
  bound U (the live emitter body + a type-safety+frame contract shape) and three disjoint
  hard lower-bound oracle planes L (mirror-sync fidelity, Why3 proof, byte-diff-0 corpus
  inertness). STATUS 2026-07: the tier-1/2/3 ADT campaign is CLOSED at count 1240 (certified
  IR-node ADT foundation banked). ON INVOCATION the loop does NOT auto-run — its FIRST action
  is to present the state + a next-move menu and ASK THE USER which to pursue (see SKILL.md
  §11 + config on_invoke_2026_07); the live track is TIER 5 value-model gaps (the 141
  trusted-pending), census-first. Use when the user says: "run the tcb reduction loop",
  "squeeze the trusted stubs", "convert the next \trusted stub", "reduce the self-annotation
  TCB", "un-trust the expression handlers", or asks to execute self-tcb-reduction.md. Plan of
  record: triage-ranked-tcb.md. Companion loop plan/ledger: self-tcb-reduction.md;
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

### 5.1 Streamlined per-stub gate (fast path — DEFAULT)

The naive per-stub gate above runs the **full self-annotation suite** (proves every mirror file) and
a **full corpus byte-diff sweep** on every stub. Both are almost entirely **redundant** and are the
loop's dominant cost — DROP them from the per-stub gate:

1. **Mirror files are proved INDEPENDENTLY.** Each mirror `.py` is its own verification program; a
   change to `identifiers.py` cannot affect `statements.py`'s proof. So the type-safety plane needs
   to re-prove **only the changed file**, not the whole suite.
2. **Mirror files are NOT in the reference corpus.** `byte-diff-sweep.sh` sweeps
   `test-suite/corpus/pycsl-reference/`; a pure-mirror conversion is byte-diff-0 **by construction**.
   A conversion that also touched the emitter (`src/pycsl/`) is a **feature** build, and its corpus
   byte-diff is gated ONCE at feature-build time — not per converted stub.

**The streamlined per-stub gate (all fast):**
```bash
# fidelity — both sync gates (seconds)
bash bin/check-self-annotate-sync.sh && bash bin/self-annotate-mirror-check.sh
# type-safety — prove ONLY the changed mirror file(s); allowlist unchanged
PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <changed-mirror-file> --import-path src/pycsl
git diff --quiet HEAD -- src/pycsl proof_axiom_allowlist.py src/self-annotate/**/proof_axiom_allowlist.py  # no emitter/axiom change in a pure conversion
# corpus inertness — by construction: assert the diff touches ONLY mirror files
git diff --name-only HEAD | grep -qv '^src/self-annotate/' && echo "NON-MIRROR CHANGE — run full byte-diff" || echo "mirror-only ⇒ byte-diff 0"
# count — must strictly shrink
find src/self-annotate/src -name '*.py' -exec grep -h '\trusted' {} \; | wc -l
```

**Batch confirmation (once per phase / per file-group, NOT per stub):** run the full
`bin/run-self-annotation-suite.sh` (no-new-failure vs the known pre-existing set) and one
`bin/byte-diff-sweep.sh` + `diff -rq` as a final belt-and-suspenders check on the whole batch. This
turns a ~10-min-per-stub gate into ~30 s/stub while keeping every soundness oracle (the batch check
catches anything the per-stub git-diff assertion could miss).

**Test-every-N amortization** (if you insist on batching the slow planes at all): keep the fast
per-stub checks per stub (they localize any failure); run the full suite only every N conversions.
A batch failure ⇒ revert the batch and bisect with the fast checks. Sound iff failures are rare —
which, with the fast per-file proof already gating each stub, they are.

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

## 9. Reference: leaf-conversion recognizers & per-leaf triage

For the *practical* how-to of individual stub conversions — the reusable recognizer stack, the
pre-conversion triage matrix, the byte-diff-inertness principles, the leak-diagnosis recipe, the known
OPEN gaps, and the efficiency rules — see **`leaf-conversion-recognizers.md`** (next to this file).
Empirical from the 1273→1266 bottom-up-DAG campaign; the DAG strategy itself is in repo-root
`giant-recursion.md`.

For the **emit_ir / AST-lowering conversion campaign** (2026-07, ~1176→1043: the entire Module5 AST→IR
lowering surface + the list-append-mutation wall-break) — the whole-file-proof-not-`--fun` gate, the
gated-emit_ir-ctor pattern, the "test boundaries by building / opaque abstract readers" doctrine, the
CONCRETE-compaction anti-vacuity rule (+ observational evil-twin fixtures), the mutable-ref append
convention, recursive-ADT encoding (mutual-cons, not `seq`/`list`), and the confirmed genuine
boundaries — see **`emit-ir-conversion-lessons.md`** (next to this file). HEED IT before any Module5/
emit_ir work; it overrides optimism about "walls" and about `--fun`.

## 10. Hard-won lessons (2026-07 tier-1/2/3 campaign — HEED THESE; they OVERRIDE optimism)

Plan of record: **`triage-ranked-tcb.md`** (this file is the loop procedure + the `self-tcb-reduction.md`
§8 ledger). The 2026-07 campaign ran the loop at scale; marker yields were **8 / 0 / 9** across three
multi-session tiers. The dominant truth: **most of the frontier is a semantic ceiling or a
soundly-trusted boundary, NOT a conversion backlog.** Convert by measurement, not ambition.

1. **CLASSIFY ON FULL `--fun` PROOF OF THE WHOLE BODY — never `--no-proof`, never an idiom in
   isolation.** The most expensive mistake, made TWICE. `--no-proof` typecheck over-counted tier-1 **5×**
   (39 "free" → 8 real). An idiom-in-isolation feasibility probe ("4/4 lower") collapsed when whole
   bodies were ported (value-model gaps + recursion-termination only surface under proof).
   **Type-check-clean ≠ proof-clean.** A stub is "convertible" ONLY when its ENTIRE real body, ported
   verbatim, discharges (`--fun` per recursive fn).

2. **MEASURE BEFORE BUILD.** Never build a multi-session feature/ADT on a *projected* yield. Run a
   whole-body feasibility CENSUS first (port → full-prove → revert → classify each stub) — cheap,
   decisive, and it repeatedly refuted large projections. Template: `getting-better/tier3/whole-body-census.md`.

3. **The frontier's real axis is REFLECTION STYLE, not node kind.** *Typed-node readers* (dispatch on
   `ir.get("type")`, project named fields) are model-addressable. *Generic-`Any`-tree walkers*
   (`for v in obj.values()` over `Dict[str,Any]`, by-ref-set mutation) are NOT modellable without a
   live-source rewrite — a **leave-trusted** class. Diagnose by style before assuming a value feature
   frees a cluster. The 141 residual "trusted-pending" stubs are dominated by 85 `Dict[str,Any]`
   generic-dict readers = this hard class.

4. **A feature that edits a VERIFIED emitter method MUST re-port + re-prove that mirror method in the
   SAME commit** (add to Gate B). Skipping it drifts the fidelity gate — the tier-2a `_handle_return_stmt`
   case: a set-model feature added IR-reflection to a verified method, the mirror couldn't re-verify,
   the feature was REVERTED (`768f5392`→`5c4b87e0`). If the re-port can't prove, the feature is gated on
   a deeper model: do NOT re-trust (a +1 regression), do NOT merge a red fidelity gate.

5. **COUPLING RULE for a feature introducing a NEW WhyML value shape** (record/variant ADT, etc.): the
   emitter capability must co-land with a `src/formal-semantics/` certificate that the new value is
   sound, or the self-annotation verifies against a construct the meta-theory doesn't cover (capability
   outrunning its certificate). **Separate two obligations, never conflate:** VALUE soundness (needs a
   co-landing certificate lemma — axiom-free; a conservative *side-car* is enough, e.g.
   `Phase2b_RecordVal.v`/`RecordVal.lean`) vs TERMINATION (a Why3-intrinsic `variant` VC, NOT a
   certificate concern). The **3-axiom ledger must stay at 3** — verify with `Print Assumptions` (Rocq) /
   `#print axioms` (Lean) after any certificate change.

6. **SINGLE-WRITER on the working tree.** Never run two mirror/emitter-editing agents concurrently — a
   stash/detached-HEAD race nearly ate committed work. The read-only triage/census probe is the ONLY
   safely-parallel actor (§8).

7. **VALUE, not count.** Convert only where a whole-body census proves it out; otherwise leave-trusted
   or demand-driven feature work. A "cheap win" that only proves the fixed `ensures True` contract adds
   no behavioral content — count it honestly.

8. **The tier-3 ADT foundation EXISTS and is certified** (feasible + sound, ledger held, independently
   reproduced): the IR-node value ADT (`preamble.py::_emit_exprir_theory`, `expressions.py`
   discriminant/projection via `_KIND_DISCRIMINANT`, `functions.py` `size`/`variant`) + the Rocq/Lean
   record-valued certificate. It covers **typed-node reads of the expr family (9 kinds)**. Extend it
   (stmt/contract families) ONLY if a census proves a worthwhile cluster — the expr census showed ≤19
   reachable of 164, so no further family was built (PATH 1).

9. **Run an INDEPENDENT ADVERSARIAL review before a big build** — it verified the certified foundation
   reproduces AND refuted the payoff projection (`getting-better/tier3/plan-review.md`), averting a
   wasted grind. Have it *reproduce* the make-or-break gates (build + axiom audit), not take them on trust.

10. **A recognizer/templater that emits its own FRAME/EFFECT from the body MUST gate on the declared
    `#@ assigns` — else the contract is unenforced for recognized methods (the frame-fidelity gap).** The
    `GenericFold` templater emitted `writes { acc }` derived from the actual mutation, silently IGNORING
    the source `#@ assigns`: a walk contract-ed `assigns \nothing` still "verified" (the emitted frame was
    correct; the annotation was decorative). The reference fixture `0884` exposed it. **Fix (`2699bc4d`):**
    the recognizer now REQUIRES the mutated accumulator to appear in the declared frame (fail-closed
    `_is_var` over `contracts.assigns`) — a wrong / `\nothing` assigns is denied the certified lowering and
    cannot verify (`0884` correctly FAILS). **Generalize:** whenever a code generator derives an effect
    (`writes`/`raises`/`variant`) from the BODY rather than the contract, add a fail-closed check that the
    CONTRACT declares it, or the recognized methods' contracts are decorative — a silent
    contract-vs-implementation hole. Lock non-vacuity with a positive/negative reference-corpus twin
    (a `assigns \nothing` negative that MUST stay unproven).

10. **The SL gate MUST include a FULL-FILE proof (`bin/run-self-annotation-suite.sh`), not just
    `--fun` + the two fidelity gates.** `--fun` proves ONE function while TRUSTING its siblings as
    `val` stubs, so a leaky *verified* method (or an emitter type-lowering bug that only bites when the
    whole file's signatures are emitted together — e.g. the `option seq int` un-parenthesized-`option`
    bug) passes `--fun` yet FAILS the whole-file proof. And `check-self-annotate-sync.sh` /
    `self-annotate-mirror-check.sh` only check body/signature MATCH, never provability. The full-file
    suite is the only plane that catches a file that type-checks per-function but is not whole-file
    provable — keep it in the gate battery, green, exit 0.

11. **When mirror files are moved/renamed, UPDATE THE SUITE ARRAY IN THE SAME COMMIT.** The suite array
    in `run-self-annotation-suite.sh` is a hand-maintained path list — a stale entry counts as
    `[MISSING]` (a failure) and, worse, silently DROPS the relocated file from the gate. The `0f0f32c7`
    regression moved 7 files to `frontend/` without touching the array: the array then listed 7 dead
    top-level paths (suite red, never exit 0) AND the relocated `frontend/` mirrors sat OUTSIDE the gate
    and drifted (`Module3_Weaver` failed whole-file proof on the `option seq int` bug, undetected for
    weeks). A move is not done until the suite array points at the new paths and still exits 0.

### 10b — driver-campaign carve-outs (runs #5–#7, 2026-07; full evidence in `getting-better/wall-lessons.md`)

These four are ledger lessons general enough to change base-loop policy, carved here per the Gate-S-lesson
protocol so they bind future runs, not just document past ones.

12. **"CONVERTED" MEANS *PORTED*, AND NOTHING ELSE — not rewritten, not truncated (wall-lesson (j)).** The
    converter's job (§4.2) is a body BYTE-VERBATIM to live. Two silent substitutes both pass every other
    gate and are NOT conversions: (a) a HAND-REWRITE — e.g. replacing live's `any(genexp)` with an
    index-counting `while` loop; it passes the mutation test and proves, but the proof covers a body the
    emitter never runs; (b) a TRUNCATION — e.g. shortening a multi-line error-message f-string so it
    lowers. Only a verbatim port supports the claim "proving the mirror proves the emitter." When a
    verbatim port cannot be made to prove, record the stub as DRIFTED (leave it `\trusted`); never book a
    green proof over a body the tool does not run. A count is only as meaningful as the body-fidelity gate
    behind it — `bin/check-self-annotate-mirror-sync.py` compares `ast.unparse` of the body (the repaired
    gate); keep it GREEN, never let it go permanently red (see 15).

13. **A `\trusted` STUB'S `#@ assigns` IS AN ASSUMPTION EVERY CALLER INHERITS (wall-lesson (f)).** An
    over-tight frame on a trusted stub is not "conservative" — it is FALSE, and any converted caller's
    proof silently rests on it (a caller's termination/frame proof can be discharged off a lie). Distinct
    from a facade: the body is real, the proof is real, only the PREMISE is fabricated, so no output-gate
    sees it. Before trusting a converted caller, RE-READ each trusted callee's declared frame against its
    LIVE body's actual (and transitive) writes. A stub with NO `assigns` clause emits as effect-free — that
    is the false claim `\nothing`, not "unspecified". (The mass-audit corollary, wall-lesson (h): before
    fixing a flagged frame family, probe the LOWERING per type — "mutates a param" is three defect classes
    with different verdicts; only the by-reference one is a soundness defect.)

14. **THE MUTATION TEST (Gate C) CANNOT SEE INT-HASH ERASURE — add the STRUCTURAL vacuity gate
    (wall-lesson (l)).** When a body int-hash-erases its input, a Python literal is emitted as its hash, so
    perturbing the literal STILL moves the emitted `.mlw` — the mutation test passes *because of* the
    erasure, over a body that never references its parameter (`IRScanner.uses_string` → `obj` appears
    nowhere; `any(genexp)` → unconstrained `any_1 (Array.make 1 0)`). This is sound-but-VACUOUS, not
    unsound. `bin/check-emitted-vacuity.py` is the gate that catches it (a body that never mentions a
    parameter its LIVE body uses); it is part of the battery — run `--emit`, require exit 0 and no NEW
    erasure. A green whole-file proof is NOT evidence the body reads its inputs. The gate covers BOTH
    parameter erasure AND self-state (wall-lesson (o)): a method is INPUT-BLIND when it references none of
    its inputs — every data param erased AND, if the live body reads a `self.<field>`, no `self`/`self__`
    token in the emitted body. NOTE the self-check is NOT a copy of the param check: a self-field is often
    encoded in the emitted BRIDGE NAME (`self__precedences_get_2`), which `\bself\b` misses — a naive check
    over-fires ~63%. Booked set measured CLEAN (0 input-blind) as of count 943.

15. **A PARTIAL method takes a GENUINE precondition — carve-out to the fixed contract shape (wall-lesson
    (d)).** The shape is `requires True / ensures True / assigns <frame>`, but a method that is genuinely
    partial in the live code (e.g. `_Parser.take` steps `self.pos` unguarded and really raises IndexError
    past the end) makes `requires True` UNPROVABLE, and the class invariant `pos < len` would be a LIE.
    `#@ requires self.pos < \length(self.toks)` — the method's REAL domain — is permitted. STRICT carve-out,
    not a licence to weaken: a precondition is allowed ONLY when it states the method's genuine partiality,
    never a convenience narrowing to dodge an unproved goal, and the class invariant must never be
    strengthened beyond what the live code actually maintains.

## 11. LOOP ENTRY — the campaign is CLOSED; the loop ASKS before working (do NOT auto-run)

The tier-1/2/3 ADT campaign is closed at count **1240** (§10). There is **no auto-run backlog.** When
this loop is invoked (Skill call, or "run the tcb reduction loop"), its **FIRST action is NOT to start
converting** — it is to **present the state + the next-move menu and ASK THE USER which to pursue.**
**The loop NEVER auto-starts a build or a conversion; the user chooses every time.** This is a hard
operating rule (the user's standing instruction), not a suggestion.

### The one remaining track — TIER 5: value-model gaps (the 141 trusted-pending)
`\trusted` stubs blocked NOT by the IR-node ADT (done) but by separate value-model gaps. Census
breakdown (`getting-better/tier3/whole-body-census.md`; residual analysis
`getting-better/tier3/step-d-leave-trusted-analysis.md`):
- **V1 — `Dict[str,Any]` value-typing (~85):** generic heterogeneous-dict reads. The HARD core —
  likely *harder* than the ADT (generic-`Any` reflection at scale). Default **leave-trusted** unless a
  census proves otherwise.
- **V2 — collection-result modeling (~43):** builders/returns whose element types aren't faithfully
  modelled — tractable via a faithful-collection feature (cf. the string-op / list work). The most
  promising cluster.
- **V3 — emitter string / self-state / WhyML-gen (~13):** mixed; SOME are actual emission **bugs to
  FIX** (a real −1 + a correctness fix), not modelling.

### The menu the loop MUST present on invocation (ask the user; default = A)
- **A — CENSUS** the 141 (or a chosen sub-class V1/V2/V3) under whole-body `--fun` proof → the measured
  tractable subset. Cheap, decisive, no build. *(Recommended first — measure before build, §10.2.)*
- **B — BUILD** one value-model feature a census proved out — fully gated: spike both provers, byte-diff
  0, whole-body proof, **a co-landing certificate lemma if it introduces a new value shape** (§10.5).
- **C — CONVERT** a specific census-confirmed cluster (streamlined gate §5.1; per-function `--fun`).
- **D — STOP** — campaign closed; the residual is a semantic ceiling / soundly-trusted. **NOT "do
  nothing":** STOP at the bounded floor is a §12 trigger — before/with proposing D you MUST produce or
  **update** the external-reviewer report with the session's measured evidence, and phrase the move as
  "hand off / refresh the reviewer report," never a bare stop.

### Tier-5 discipline (all of §10 applies)
Census-first, demand-driven, **VALUE not count**, single-writer, whole-body proof, coupling/3-axiom-ledger
for any new value shape. **Do NOT re-open this as a marker campaign** — expect a small tractable slice
(V2/V3), with V1 mostly leave-trusted. Whatever the user picks, gate it exactly as §3/§5.1/§10 require,
and append the outcome to `self-tcb-reduction.md` §8.

## 12. AT A RESEARCH-GRADE BOUNDARY — auto-produce an external-reviewer report (STANDING RULE; do NOT wait to be asked)

**Trigger (any of these — not only the first):**
1. the moment you are about to characterize a residual as *"research-grade / needs a new value
   model / an unbounded capability / not a bounded fold / a distinct multi-session feature"* — a wall
   that is NOT a bounded engineering fix; **or**
2. **cumulative convergence** — when a session's *multiple* measured censuses/spikes all refute their
   bounded leads and **converge on the SAME wall** (e.g. "every lead dissolves into the read's
   composition"). The convergence IS the research-grade characterization, even if no single step said
   "research-grade"; **or**
3. **whenever the loop is about to recommend STOP / menu-option D because "the bounded frontier is
   exhausted."** Reaching the bounded floor IS a research-grade boundary.

**STOP-implies-report (the rule the user strengthened).** At any of these triggers you must **STOP and
produce OR UPDATE the standalone external-reviewer report before moving on** — and the close-out move you
PROPOSE to the user must be *"produce/update-and-hand-off the reviewer report"*, **not a bare "stop."**
Recommending STOP (or writing "this is research-grade / the floor is N" in a status/ledger) WITHOUT
producing-or-updating the report **and** offering it as the close-out is a **process error**. The user
must never have to ask for it (they have asked repeatedly — `generic-dict-str-and.md`,
`generic-dict-str-any-2.md`, `wall-plan-v2-phase2c-stand-alone.md`, `value-model-wall-stand-alone.md` —
make it automatic).

**Keep-current (a stale report is as much a process error as no report).** If a report for this wall
ALREADY exists, you do NOT skip §12 — you **UPDATE it** with the session's new measured evidence: every
census/spike that sharpened the wall (which lead was refuted and how, verbatim errors, what is now
newly-SOLVED/certified, the tightened benchmark). A report that predates the session's measurements and
no longer reflects the sharpened wall must be revised in the same close-out. State in the menu that the
proposed move updates the *existing* report by name.

**The report MUST be:**
- **Self-contained** — submittable to an external PL / deductive-verification / verified-compilation
  reviewer with ZERO project context (define PyCSL, the pipeline, the terms).
- **Globally framed — ALWAYS describe the global problem, never just the local symptom.** Situate it in:
  the self-verification bootstrap (PyCSL verifying its own emitter), the **3-axiom Rocq 8.20 + Lean 4.29
  ledger** + the coupling rule (new value shapes co-land an axiom-free certificate), **LINK-1/2/3**, and the
  decisive **type-safety + frame-only scope cut** (never value-faithful) that keeps the problem bounded.
- **A measured statement of the issues** — the exact obstacles with EVIDENCE (what was tried, verbatim
  errors, both-prover results), AND what is already SOLVED/certified (so the reviewer doesn't re-solve it).
- **A request for state-of-the-art comparison** — enumerated open questions, each tagged with candidate
  SOTA anchors so the reviewer maps techniques onto the stated constraints.
- **A frozen benchmark / success criteria** — the exact reproducible artifacts a proposal must clear; state
  that a rigorous "no technique can, under these constraints" is an equally valuable closure.

**Templates (copy their shape):** `generic-dict-str-and.md` (internal wall report), `generic-dict-str-any-2.md`
and `wall-plan-v2-phase2c-stand-alone.md` (external-reviewer statements). Store at repo root with a
descriptive name; commit it. This is the honest close-out of a research-grade boundary: **bank the measured
certified foundation, hand the sharp well-posed open question to a reviewer, and stop grinding** — rather
than burning session-momentum on a wall the loop cannot cross with bounded work.
