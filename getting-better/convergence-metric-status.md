# Convergence metric implementation — status
LAST-UPDATED: 2026-09-13T16:20:00Z
PHASE-1-PROBE-LEDGER: DONE
PHASE-2-VERIFIED-FRACTION: DONE
PHASE-3-REASON-TAXONOMY: NOT-STARTED
PHASE-4-SILENT-RAISE-BURNDOWN: NOT-STARTED  (70 -> 70)
PHASE-5-BLIND-RECAPTURE-RUNBOOK: NOT-STARTED
PHASE-6-GENERATED-SAMPLER: NOT-STARTED
OVERALL: INCOMPLETE
NEXT-ACTION: Phase 3 PILOT — tag `reason:` on the ONE mirror file with the fewest markers, then why3 --type-only + emission byte-diff + both fidelity scripts. IF EMISSION MOVES BY ONE BYTE: STOP, do not tag the other files, write it up as a FINDING, mark Phase 3 BLOCKED:emission-moved.
NOTES:
- Phase 1 at 10e58637. probes.tsv 145 rows; bin/probe-ledger-yield.sh; all three prose yield
  figures reproduce exactly. Back-fill is ASYMMETRIC — cross-generation yield from it is NOT
  valid, only the carve-out-census rows are. Caveat is in the TSV header.
- THE DRIVER RULE IS ON DISK IN getting-better/.driver-worker-prompt.md BUT THAT FILE IS
  GITIGNORED, so it is not version-controlled. Re-check it exists before relying on it.
- Phase 2 at 5774b32a (+ fea721a9 prose repair). bin/verified-fraction.py;
  bin/count-trusted-directives.py --metrics delegates to it; default path untouched (rc=0,
  markers 459 / grep 484 / offset 25 / unattached 0).
- THE CORRECTED VERIFIED-FRACTION TRIPLE (bin/verified-fraction.py --staleness=file):
      (1) verified / live      499 / 3225 = 15.47 %
      (2) unproven-perimeter   644 defs in 27 of 53 mirror files
      (3) unmirrored ratchets  MAX_UNMIRRORED_DEFS=549  MAX_UNMIRRORED_FILES=41
          OLDEST PROOF RELIED ON  2026-09-02
          FALSIFICATION GUARD     OK (did not rise since HEAD~1)
  vs the report's 914/3236 = 28.2 %. Population: 26 PROVED / 7 STALE / 18 NO-PROOF / 2 FAILED.
  THE STRICT FLOOR IS 0.00 % (--staleness=strict): no proof in the repo survives a single
  commit to src/pycsl, and the driver commits several times a day.
- STATED LIMITATION of Phase 2: proof run time is the log file's mtime, a proxy a copy would
  inflate. Checked by hand that mtimes are spread over genuine run times, not bulked.
- THE DRIVER IS LIVE (route #99 landed at 275146d9 during this spawn; one .git/index.lock
  collision already hit and was resolved by waiting 20 s). RE-CHECK THE BOX BEFORE PHASE 3/4/6.
