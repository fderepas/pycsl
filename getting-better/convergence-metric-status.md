# Convergence metric implementation — status
LAST-UPDATED: 2026-09-13T16:45:00Z
PHASE-1-PROBE-LEDGER: DONE
PHASE-2-VERIFIED-FRACTION: DONE
PHASE-3-REASON-TAXONOMY: BLOCKED:box-busy
PHASE-4-SILENT-RAISE-BURNDOWN: BLOCKED:box-busy  (70 -> 70, no edits made)
PHASE-5-BLIND-RECAPTURE-RUNBOOK: DONE (runbook only, per scope limit)
PHASE-6-GENERATED-SAMPLER: DONE-AUTHORING / BLOCKED:box-busy for the sweep
OVERALL: INCOMPLETE
NEXT-ACTION: Box-check first. If idle, run the Phase 3 PILOT on src/self-annotate/src/frontend/exec_splice.py line 35 (recipe below). If emission moves by ONE BYTE: STOP, do not tag the other files, write it up in getting-better/open-routes/ style, mark PHASE-3 BLOCKED:emission-moved.

## SUPERVISOR SCHEDULING POLICY — SET BY THE USER 2026-09-13 ~18:35Z
THE DRIVER IS PAUSED BETWEEN GENERATIONS TO GIVE THIS WORK THE BOX.
When the current driver generation finishes, the supervisor spawns THIS implementation
agent FIRST and lets it take one increment on an idle box, THEN launches the next driver
generation. Rationale: Phases 3, 4 and the Phase-6 sweep need an idle box; the driver
campaign runs suites/planes/proofs back-to-back for the whole 96h window, so waiting for a
natural gap never fires. The between-generation gap is free box time.
PRIORITY ORDER ON AN IDLE BOX: Phase 3 pilot -> Phase 3 tagging -> Phase 4 burn-down.
The Phase 6 sweep is LAST and may be deferred to after the window closes (Thu Sep 17).
Take ONE increment, leave the tree clean and committed, update this file, and stop — do not
hold the box longer than the increment needs; the driver is waiting on you.

## COMMITS
  10e58637  Phase 1 — probe ledger + yield reporter + driver rule
  5774b32a  Phase 2 — verified fraction from proof verdicts   (fea721a9 prose repair)
  758fc276  Phase 5 — blind recapture runbook
  184f81cb  Phase 6 — generated differential sampler (authored, not swept)

## THE CORRECTED VERIFIED-FRACTION TRIPLE  (bin/verified-fraction.py --staleness=file)
      (1) verified / live      499 / 3225 = 15.47 %
      (2) unproven-perimeter   644 defs in 27 of 53 mirror files
      (3) unmirrored ratchets  MAX_UNMIRRORED_DEFS=549  MAX_UNMIRRORED_FILES=41
          OLDEST PROOF RELIED ON  2026-09-02
          FALSIFICATION GUARD     OK — did not rise since HEAD~1
  Report's figure was 914/3236 = 28.2 %. Population: 26 PROVED / 7 STALE / 18 NO-PROOF /
  2 FAILED. STRICT FLOOR IS 0.00 % (--staleness=strict): no proof in this repo survives a
  single commit to src/pycsl, and the driver commits several times a day.

## PHASE 3 PILOT RECIPE — READY TO RUN, DO NOT DEVIATE
  PILOT FILE: src/self-annotate/src/frontend/exec_splice.py
    Chosen because it has exactly ONE real marker (line 35, inside `_ExecSplicer`) AND a
    passing whole-file proof on record (w49_exec_splice, rc=0), so there is a baseline and
    a re-proof is cheap. Three other files also have 1 marker — exception_model.py,
    ir_schema.py, module6_whyml/expr_ghost_collections.py — but all three are NO-PROOF.
    NOTE: line 4 of the file contains the marker text inside the MODULE DOCSTRING. That is
    one of the 25 known offset lines. DO NOT EDIT LINE 4 — edit only line 35.
  EDIT: append ` reason:<bucket>` to line 35 only.
  THEN, IN ORDER:
    1. why3 prove --type-only on the edited mirror
    2. emit that file's .mlw and diff against HEAD — MUST BE BYTE-IDENTICAL
    3. bash bin/check-self-annotate-sync.sh      — delta ZERO
    4. bash bin/self-annotate-mirror-check.sh    — delta ZERO
  IF EMISSION MOVES BY ONE BYTE: STOP. That is a comment-level token changing emission,
  which is route-shaped and is the #96 pattern. Write it up as a FINDING and stop Phase 3.

## NOTES
- THE DRIVER IS LIVE AND THE BOX HAS BEEN BUSY SINCE ~16:25Z: `bin/run-reference-tests.sh
  --jobs 6` (suite99), VERDICT=ALIVE, 35 live processes. Phases 3, 4 and the Phase-6 sweep
  are BLOCKED on it. A later spawn will find it free. Route #99 landed at 275146d9 during
  this spawn and is already in probes.tsv.
- .git/index.lock collided twice with the driver; both resolved by waiting 20 s and
  retrying. Never delete the lock.
- THE DRIVER RULE IS ON DISK IN getting-better/.driver-worker-prompt.md BUT THAT FILE IS
  GITIGNORED, so it is NOT version-controlled and is not in any commit. A successor must
  re-check it exists before relying on it.
- PHASE 1 BACK-FILL IS ASYMMETRIC. Every LIVE row was recoverable; FAIL-CLOSED rows exist
  only where a generation wrote a no-finding section. So w49/4/11/16/17 and
  generator=unknown read ~100 % yield as an ARTEFACT OF THE RECORD. Only the
  carve-out-census rows are safe to compare across generations. DO NOT quote the 41.5 %
  aggregate as "the yield". Caveat is in the TSV header.
- PHASE 1 SCHEMA DEFECT FOUND BY ITS OWN ACCEPTANCE TEST and recorded, not silently fixed:
  two probes had been filed OUT-OF-SCOPE because CPython raises, when the record says they
  were RUN AND REFUSED. Rule now: verdict records what the MEASUREMENT returned.
- PHASE 2 STATED LIMITATION: proof run time is the log file's mtime, a proxy a copy would
  inflate. Checked by hand that mtimes are spread over genuine run times, not bulked.
- PHASE 5 FINDING: the blind is STRUCTURALLY PARTIAL. Withholding the three documents the
  report names is NOT sufficient — 271 corpus witness filenames, 20 differential drivers,
  367 commit subjects, 88 getting-better files and 27 src/ files name routes. The last two
  cannot be withheld without changing the artefact under study (src/ names routes in its own
  comments, and reading the emitter IS the hunter's method). Partial sight raises m, which
  lowers N-hat — the SAME direction as the shared-method bias, so the two COMPOUND.
- PHASE 3 IS BIGGER THAN THE PLAN IMPLIES. `unclassified -> 0` is the stated acceptance,
  but driver-backlog.md carries only 4 `[CORRECTNESS]` and 17 `[COST/SCALE]` tagged
  paragraphs against 459 markers across 45 files. Most markers will start `unclassified`
  and driving that bucket to zero is a multi-generation task, not "one pass over 459 lines".
  Say so when Phase 3 lands rather than tagging speculatively — a `correctness:` tag is a
  CLAIM, and this repo's boundary claims have been refuted repeatedly.
- PHASE 4 HAS NOT STARTED AND MAX_SILENT HAS NOT BEEN TOUCHED (still 70). When it starts:
  order batches by the cheap property gen #16 measured — a `raises` on a val declared but
  never called in-file adds no VC. NEVER raise MAX_SILENT to make the ratchet pass.
