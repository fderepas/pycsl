# Convergence metric implementation — status
LAST-UPDATED: 2026-09-13T15:55:00Z
PHASE-1-PROBE-LEDGER: DONE
PHASE-2-VERIFIED-FRACTION: IN-PROGRESS
PHASE-3-REASON-TAXONOMY: NOT-STARTED
PHASE-4-SILENT-RAISE-BURNDOWN: NOT-STARTED  (70 -> 70)
PHASE-5-BLIND-RECAPTURE-RUNBOOK: NOT-STARTED
PHASE-6-GENERATED-SAMPLER: NOT-STARTED
OVERALL: INCOMPLETE
NEXT-ACTION: Phase 2.2 — recompute verified defs from getting-better/proofs49/*.rc verdicts, NOT from marker absence. Publish the triple + oldest-proof date.
NOTES:
- Phase 1 landed at commit 10e58637. probes.tsv = 145 rows (56 LIVE / 79 FAIL-CLOSED /
  6 VACUOUS / 2 INCOMPLETE / 2 OUT-OF-SCOPE). Reporter: bin/probe-ledger-yield.sh.
  All three prose yield figures reproduce exactly (see commit message).
- THE DRIVER RULE WAS WRITTEN TO getting-better/.driver-worker-prompt.md BUT THAT FILE IS
  GITIGNORED, so it is on disk but NOT in the commit. A successor must not assume it is
  version-controlled; re-check it exists before relying on it.
- The back-fill is ASYMMETRIC (numerator complete, denominator only where a generation wrote
  a no-finding section). Cross-generation yield from back-filled rows is NOT valid; only the
  carve-out-census rows are. Caveat is in the TSV header. Do not quote 41.5%% as "the yield".
- THE DRIVER IS LIVE: it committed route #99 at 275146d9 during this spawn. Box checks
  returned VERDICT=NOWORKER and no live provers, but RE-CHECK BEFORE EVERY HEAVY PHASE.
