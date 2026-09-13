# RUNBOOK — the blind recapture window (Phase 5 of `convergence-metric-implement.md`)

**STATUS: RUNBOOK ONLY. THE WINDOW HAS NOT BEEN RUN AND MUST NOT BE RUN FROM THIS
DOCUMENT.** Producing a genuinely blinded sampler is the human supervisor's call, because
the blind is only as good as the withholding, and §4 below shows the withholding cannot be
made complete. Nothing here spawns an agent.

This is the campaign's only proposed instrument that estimates the population **not yet
found**. Everything else counts what was found.

---

## 1. What it is

Lincoln–Petersen capture–recapture. Two samplers hunt the same population. Sampler 1 is the
driver, whose catch `n₁` is the route ledger. Sampler 2 is a fresh agent window that has
never seen the ledger, with catch `n₂`, of which `m` are routes the driver already knows.

    N̂ ≈ n₁ · n₂ / m        and       remaining ≈ N̂ − (routes known)

The value of the exercise is **not** `N̂`. It is `m / n₂`, and the asymmetry of what that
ratio can tell you (§5). `N̂` itself is biased and the bias runs the dangerous way (§5.2).

---

## 2. Setup

* **HEAD.** A clean tree at a named commit. Record the SHA in the result; a blind window run
  against a different tree than the ledger describes measures nothing.
* **Budget: 40 probes, fixed in advance, and not extended for a promising lead.** The budget
  must be fixed before the window opens or `n₂` is a function of how interesting the window
  turned out to be, which destroys the estimator.
* **Same rules as the driver**, so that the two samplers are hunting the same population:
  * CPython is ground truth.
  * Every candidate probed **in both directions** — the false claim must be refused *and*
    the true twin must prove. A one-direction probe is not a probe.
  * **A probe whose positive control refuses is `VACUOUS` and measured nothing.** It is not
    a clean negative, and it does not consume budget as a `FAIL-CLOSED`. Log it as VACUOUS.
* **Every probe appends a row to a SEPARATE ledger**, `getting-better/open-routes/
  probes-blind.tsv`, same schema as `probes.tsv` with `generator=blind`. It must be
  separate: merging it into the driver's ledger before the readout would let the blind
  hunter's rows be compared against the ledger it was supposed not to see.

---

## 3. What must be withheld — the explicit list

The report names three things ("the route ledger, handoff and progress log"). That is not
sufficient. Measured at HEAD:

| surface | how many name a route | withholdable? |
|---|---|---|
| `getting-better/open-routes/**` (route files, findings, README, `probes.tsv`) | all | YES |
| `getting-better/driver-handoff-latest.md` | — | YES |
| `getting-better/driver-progress.log` | — | YES |
| `getting-better/driver-backlog.md` | — | YES |
| `getting-better/.driver-worker-prompt.md` (names the live generators AND the open route) | — | YES |
| other `getting-better/*.md` | **88 files** | YES |
| `test-suite/corpus/pycsl-reference/*route*.py` | **271 files** | yes, but see §4 |
| `test-suite/value-differential/*route*.py` | **20 files** | yes, but see §4 |
| `docs/`, `test-suite/*.md` | 4 files | YES |
| **git history — commit subjects naming a route** | **367 commits** | **NO — see §4** |
| **`src/` comments naming a route** | **27 files** | **NO — see §4** |

Commands (run these fresh; the numbers move every generation):

```
ls test-suite/corpus/pycsl-reference | grep -ci route
ls test-suite/value-differential | grep -ci route
git log --oneline | grep -ciE 'route ?#[0-9]+'
grep -rliE 'route ?#[0-9]+' src/ | wc -l
grep -rliE 'route ?#[0-9]+' getting-better/ | wc -l
```

Mechanically: give the window a worktree with the withholdable paths removed, a shell whose
`git log`/`git show` are unavailable, and a task prompt that states the CPython-ground-truth
rule and the 40-probe budget and **nothing about what has been found**.

---

## 4. THE BLIND IS STRUCTURALLY PARTIAL, AND THE RUNBOOK SAYS SO BEFORE THE NUMBER IS QUOTED

Two leaks cannot be closed without destroying the measurement:

1. **`src/` carries route numbers in its own comments — 27 files.** Samples measured at HEAD:
   `route #51's Module 6`, `route #44's opaque pycsl_none`, `route #93 — the comment here
   used to say "the only opt-out"`, `route #91`, `route #92`. The blind hunter's *method* is
   reading the emitter. Stripping those comments changes the artefact under study — and a
   comment is exactly where this campaign keeps finding routes (the carve-out census, the
   deferral census, `#98`'s "stays visible"). **You cannot blind the hunter to the object it
   is hunting in.**
2. **Git history names 367 routes in commit subjects.** A worktree without `.git` is
   possible, but it also removes the ability to see what changed and when, which is part of
   the driver's method too.

**Consequence, and it must be stated next to `m/n₂` every time:** the blind sampler is
*partially sighted*. Partial sight raises `m` — it steers the blind hunter toward ground the
driver has already worked — which lowers `N̂` and makes the remaining population look
smaller. That is the **same direction** as the shared-method bias of §5.2. The two biases
compound, and both flatter the campaign.

So: **`m/n₂` measured this way is an upper bound on the true overlap**, and `N̂ − known` is a
lower bound on what remains. Report it as such or do not report it.

---

## 5. The readout, and the ONLY interpretations permitted

Report exactly three numbers plus the HEAD SHA:

    n₂ = the blind window's LIVE findings
    m  = how many of those are routes the driver already knows (closed OR open)
    m / n₂

### 5.1 The three verdicts

* **`m/n₂` LOW → STRONG EVIDENCE AGAINST CONVERGENCE.** This is the informative direction
  and the reason to run the window at all. The blind hunter keeps finding things the driver
  did not, so the population is not exhausted. It also hands you a concrete deliverable: the
  list of **generators the driver lacks**. Write that list into the handoff.
* **`m/n₂` HIGH → WEAK EVIDENCE *FOR* CONVERGENCE. NEVER "NEARLY DONE".** Shared method
  inflates `m`, partial sight (§4) inflates `m` again, and both deflate `N̂`. A high overlap
  is consistent with convergence and equally consistent with two hunters sharing the same
  blind spot. Quote it only with the bound: **`N̂ − known` is a LOWER BOUND on what remains,
  never an estimate of completion.**
* **`n₂ = 0` → NO MEASUREMENT. NOT CONVERGENCE.** Identical to a probe whose positive
  control refused, and to route #94's empty population: an instrument that found nothing has
  said nothing about the population. Record it as an **uninformative sample**, say why (the
  budget, the generators the window chose, whether its positive controls fired at all), and
  do not let it appear anywhere as evidence the hunt is finishing.

### 5.2 Why the bias runs the dangerous way

Two agents reading the same emitter with the same skill share a *method*. Independence in
Lincoln–Petersen is about **information**, not about method. Shared method makes the two
catches overlap more than two genuinely independent samplers would; excess overlap inflates
`m`; inflated `m` deflates `N̂ = n₁·n₂/m`. The estimator therefore **systematically
under-estimates what remains and reports "nearly done" too early.** For a soundness
campaign that is the wrong direction to be wrong in, which is why the high reading is
demoted to weak evidence and the low reading is promoted to strong.

---

## 6. Scheduling

Needs prover time. **Run only on a quiet box — never during the reference suite, and never
alongside more than the campaign's standing ceiling of ~4 concurrent whole-file proofs.**
Check before opening the window:

```
ps -eo pid,etimes,cmd | grep -E 'pycsl\.py|why3|run-reference-tests|byte-diff' | grep -v grep
bash bin/driver-supervise-check.sh 2>&1 | tail -3
```

Cadence: once per two or three generations (per §3 of the implementation plan).

---

## 7. What this measurement still cannot see

* Defects **neither** sampler's method reaches. Two agents reading the emitter is one method
  sampled twice, however well blinded.
* The refusal-text surface. `#90` came from a remediation message's *prose*, and no
  program-level hunter samples English.
* Whether a route the blind hunter files as new is genuinely new, or an already-closed route
  it rediscovered under a different name. The `m` count requires a human adjudication pass
  against the ledger **after** the window closes, and that pass is where `m` is actually
  decided. Budget for it.
