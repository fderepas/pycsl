# Driver run #5 plan: batched proofs, `\trusted` reduction as the main track

Status: APPROVED by the user 2026-11-04 (during run #4), with a THIRD PROOF SLOT allowed (see §5).
Applies to: the next 96 h `self-tcb-reduction-driver` run, branch `ghost-assign-bc6`, commit-only (no push).

## 1. Why change

In run #4 (2026-10-31 14:35Z to 2026-11-04 14:35Z), `\trusted` fell only 417 -> 415: `parser.py::lex`
(log 382) and `module6_whyml/identifiers.py::whyml_ident` (log 428). Most of the time went elsewhere:

- **Soundness repair, not TCB reduction.** Six red-team rounds (rt48-rt53) each confirmed 250-340 CPython
  breaches, which became routes #506-#564. Each round cost 2-4 repair executors, an integration tree and a full
  battery. Those landings never move the `\trusted` count.
- **Whole-file mirror proofs per conversion.** `lex` alone owed six whole-file proofs, among them
  `expressions.py` (6h04m) and `statements.py` (5h19m), and they ran one conversion at a time.
- **One shared proof queue.** heavy.sh has 2 proof slots (1 NORMAL, 2 LOW) plus QUICK slot 3. With 4-5 users,
  30-40 min waits were routine.
- **Capability is the real blocker.** The log 393 survey found 25 stubs that could use the `lex`
  capabilities, all blocked by some other missing piece. The cheap queue was empty (cv7, log 411).
  Converting `whyml_ident` needed three new capabilities.

Target realism: 415 -> 200 means about 215 conversions, which is not reachable in one 96 h run. Run #5 aims to
**maximise conversions per whole-file proof hour**. A reasonable success bar is **at least 15 conversions
(415 -> 400 or lower)**, plus a ranked capability backlog that makes the next runs faster.

## 2. The new loop: capability batches

Each iteration is one **batch**: one capability, or a small set, plus every stub it unblocks.

1. **Census, cheap (QUICK slot only).** For each `\trusted` stub, record:
   - its *first blocking link*, using `--no-proof` / `--type-only` emissions only;
   - the mirror files its conversion would move.

   Write the result to `getting-better/run5-capability-census.md`, with one row per stub:
   `stub | file | first blocker | capability id | mirror files moved`.
2. **Rank capabilities by yield.** Score each capability by:
   - the number of stubs whose first blocker it removes;
   - weighted down by its estimated whole-file proof cost (the sum of the movers' last measured proof times);
   - weighted down by soundness risk.

   Pick the top one or two.
3. **Build the capability** in one executor tree (the `lx` / `lv` spike pattern). Rules:
   - small, sound and axiom-free;
   - law-free `val function`s are allowed;
   - no new `\trusted`;
   - refuse rather than approximate.
4. **Convert every stub it unblocks** in the same tree, up to the batch cap (§3). Do it in parallel executors
   when the stubs sit in different files.
5. **Cheap gates on every single conversion** (unchanged, mandatory, never batched):
   - the `--fun` proof of the converted function: 0 non-Valid, 0 facades;
   - the corpus byte-diff, root + pyref: 0 MOVED, or only declared movers;
   - mirror-sync fidelity: rc 0;
   - the fast planes, including mirror-coverage and the vacuous-drivers check;
   - ledger == 3.
6. **Batched expensive gates, once per batch** on the integrated batch tree (§3):
   - each moved mirror file is proved whole-file exactly once;
   - then one `--slow` battery and the witness re-runs (default / typed / store).
7. **Land the batch**, then log it and remove the worktrees.

## 3. Batching rules for the expensive proofs

- **Batch cap.** A batch closes when either:
  - it holds 6 conversions; or
  - its owed whole-file proof time reaches about 12 h of single-slot time, using the last measured times
    (`expressions` ≈ 6 h, `statements` ≈ 5.3 h, `pure_ast` ≈ 1 h, `identifiers` ≈ 20 min, `pycsl` short).

  Whichever comes first closes the batch.
- **One proof per moved file per batch.** If three conversions all move `expressions.py`, prove it once, after
  the last of the three is merged, not three times.
- **Order the proofs short-first.** Prove the short movers first, so most failures appear early. The 5-6 h
  files go last.
- **Bisect on failure.** If a batched whole-file proof fails, do not re-prove the whole file per conversion.
  Instead:
  1. run `--fun` on each converted function in that file against the integrated tree, which is cheap;
  2. read which goal failed;
  3. drop the offending conversion from the batch (keep it on its branch as WIP);
  4. re-prove the file once.

  Record the bisect cost in the log, so that if bisects turn out frequent, the batch cap gets smaller.
- **Avoid hot files.** Where possible, choose capabilities whose conversions do not move `expressions.py` or
  `statements.py`. If those files must move, group *all* the conversions that touch them into one batch.

## 4. Red-team cadence (reduced, not removed)

The soundness work matters, but in run #4 it took over the run. For run #5:

- **When to run a round.** One red-team round per *two* landed batches, and at most one round in flight at a
  time.
- **Scope.** The round attacks *what the batches changed*: the new capabilities and the converted functions'
  emission, plus a short convergence check on the latest repairs. It does not attack fresh unrelated axes.
- **Triage the confirmed breaches:**
  - **Introduced by a run #5 capability:** repair immediately. This is mandatory, and the capability's batch
    is not "done" until it is fixed.
  - **Pre-existing (outside run #5's changes):** open the route, then put it in a `repair-backlog` that gets
    one repair executor at a time. That executor runs only when it does not delay a batch's proofs.

  The point is that a pre-existing soundness hole no longer pre-empts the TCB track.
- **Carry-over from run #4.** Keep routes #556, #558, #560-#562 and u21's documented `Optional[Tuple]`
  residual in that backlog.

## 5. Heavy-queue allocation

- **Third proof slot (user-approved 2026-11-04).** At run #5 start, add slot 4 to heavy.sh: NORMAL uses slots 1 / 4, LOW uses 2 / 4, QUICK stays on 3. The slice cap stays 9 GB with 6 GB per job. Install it by writing a new file and `mv`-ing it over heavy.sh, never by editing in place (the 2026-10-16 deadlock rule). Do not change it while run #4's jobs are queued. If any OOM kill or slice-cap hit happens, drop back to 2 proof slots and log it.
- **Slots 2 and 4 (LOW)** run the batch's whole-file proof queue, with two files in parallel. The two longest files (`expressions`, `statements`) never run at the same time, to stay under the 9 GB slice cap.
- **Slot 1 (NORMAL)** is for the cheap per-conversion gates. Backlog repair and red-team proofs take it only
  when no batch gate is waiting.
- **Slot 3 (QUICK)** is for the census and capability spikes, which run `--no-proof` only.
- **The heavy.sh rule is unchanged:** every heavy job goes through heavy.sh, and no bare CPython overflow
  probes (the run #4 OOM carve-out).

## 6. What stays exactly as in run #4

- The three L-planes as the acceptance oracle, so no plane is weakened: byte-diff inertness, Why3 proof and
  mirror-sync fidelity. Run #5 changes **when** the expensive plane runs, not **whether** it runs.
- Commit-only (never push), the integration-tree discipline (`intN` + `vN` battery before landing),
  driver-side re-proof of executor claims, worktree housekeeping, and hourly status entries in
  `getting-better/driver-run-log.md`.

## 7. Day-by-day shape (96 h)

| Phase | Hours | Work |
|---|---|---|
| Census | 0-6 | Capability census on QUICK, ranking, pick batch A; land u24 / int30 leftovers from run #4 if not landed |
| Batch A | 6-30 | Build capability A, convert its stubs, cheap gates, batched proofs, land |
| Batch B | 24-54 | Start building B while A's proofs run (they overlap on different slots) |
| Red team 1 | ~54 | Covers A and B |
| Batch C | 54-80 | Plus backlog repairs in spare slot-1 time |
| Wrap-up | 80-96 | Last batch must close its proofs by hour 90; red team 2 report-only; final report |

## 8. Decisions for the user before run #5

1. ~~Approve this plan~~ APPROVED 2026-11-04, with the batch cap as proposed.
2. **Red-team cadence:** one round per two batches (proposed), per batch, or report-only.
3. ~~Heavy queue~~ DECIDED 2026-11-04: a third proof slot is allowed (§5). The machine has 15 GB RAM, the slice
   cap is 9 GB with 6 GB per job, and typical use was 1-4 GB.
4. **Still-pending items from run #4:**
   - #429 Latin-1;
   - #414 MemoryError;
   - `PyCSLError.__init__` `requires line >= 0`;
   - #461 top-level execution;
   - the severities of #461 / #488;
   - the dict-model boundary / #UND;
   - `declared_in` as a counted class;

   #497 matters most here: an `\abstract` policy could let some stubs drop `\trusted` without a full body proof.
