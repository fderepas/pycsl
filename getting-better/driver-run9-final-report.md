# Driver run #9: final report (self-tcb-reduction-driver, AUTONOMOUS, 96 h)

DRAFT (written during the run; finalised at the deadline; see the last log entries for the end state).

- **Window:** 2026-11-21T21:25:23Z to 2026-11-25T21:25:23Z (`.driver-deadline` = 1795641923).
- **Branch:** `ghost-assign-bc6`. COMMIT-ONLY: nothing was pushed.
- **Run log:** entries 1269-END in `getting-better/driver-run-log.md`.
- **Interruptions:** API weekly rate limit (~07:25Z-11:24Z 2026-11-23, log 1325/1326); user PAUSE 20:31Z-22:10Z 2026-11-23 (logs 1346-1349); two /tmp user-quota incidents (21:35Z and 22:27Z 2026-11-23, logs 1349-1352; all driver / executor jobs moved to a TMPDIR on the repo volume).

## 0. Read first (soundness)

- **No VACUOUS verdict anywhere** (51 mirror whole-file proofs under the final probe tooling, every red-team round, every gate).
- **Priority 1 is done:** main no longer fails its own gate on the `is_pstr` probe (L19: u62 + u63; 7 badly built probe shapes fixed; type-only census 0 rejected over 5430 emissions / 16771 probes).
- **Many PRE-EXISTING false proofs were found and closed** (routes #619-#636; see §4). Still OPEN pre-existing false proofs: v1f, V1D, #634 (cross-module `assigns \nothing`), #637-#642 (see §8).
- **Two introduced false proofs were caught by red teams before landing and repaired** (u66's s1 / s8, fixed by u69; u74's F1, being repaired by u76 — see §2).

(Sections 1-9 are completed at the end of the run.)

## 9. Run #10 inputs

- The run #10 brief is `getting-better/run10-brief.md` (commit 9f83c3b0c, written by the supervisor on the user's request: \trusted reduction first; L24 = run9-u77 lands first if run #9 does not land it). Its "Open inputs" list is kept current by dated lines appended by this driver before the deadline.
