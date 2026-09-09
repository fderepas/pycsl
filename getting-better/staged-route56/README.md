# STAGED — ROUTE #56's WITNESSES AND ITS REPAIR, HELD OUT OF THE TREE ON PURPOSE

These three corpus files are FINISHED and MEASURED. They are parked here rather than in
`test-suite/corpus/pycsl-reference/` for one reason, which is the campaign's own rule:

> Move each file into the corpus in the SAME increment that closes its route.
> (`getting-better/open-routes/README.md`) — because a corpus witness for an OPEN route
> is an **XPASS**, and the harness has counted an XPASS as a failure since relaunch #44.

Route #56's repair is a `src/pycsl/module6_whyml/expressions.py` change, and it CANNOT
land while a reference suite is live: the runner spawns a fresh subprocess per test that
imports the LIVE emitter, so any edit after the suite starts contaminates it (runs 2, 3
and 4 of window #50 were each killed for exactly this). Reference-suite run 6 has been
live since 12:08 UTC and its job is to confirm the route #42 re-fix, which is a
measurement I am not willing to degrade.

## THE LANDING SEQUENCE, IN ORDER

1. Wait for `getting-better/proofs49/suite49_run6.rc`. Record its verdict FIRST —
   `1053`/`1054`/`1055` must be back at CONFIRMED FAIL.
2. Apply the repair: in `_union_read_projection`
   (`src/pycsl/module6_whyml/expressions.py`, the `else: _sentinel = "0"` fall-through),
   emit `self._add_abstract_op("val function pycsl_none : int")` and use `pycsl_none` as
   the sentinel. MEASURED in an isolated worktree: the route witness goes from
   `[+] SUCCESS` to `[-] FAILED`, the `x == 5` precision control still proves, and the
   `is None` guard still proves.
3. `git mv` these three files into `test-suite/corpus/pycsl-reference/`.
4. Run the L3 byte-inertness plane — `bin/byte-diff-sweep.sh` twice plus
   `bin/byte-diff-compare.py`, which since `681acc25` fails on MOVED / GONE / **APPEARED**.
   This is the step that is NOT yet done and it is the one that could still change the
   verdict: the mirror does carry `Optional`-annotated locals, so the repair is NOT
   obviously byte-inert and may owe mirror re-proofs.
5. Re-run `bin/run-soundness-planes.sh` and the 30th plane
   (`bin/check-type-keyed-value-sentinels.py`, whose baseline already carries #56's entry).

## THE FILES

  * `1108_…_none_is_zero.py`  — the NEGATIVE witness (`# pycsl-expected: FAIL`). At HEAD it
    PROVES `\result == 0` where Python returns 9. After the repair it must fail closed.
  * `1109_…_guard_still_faithful.py` — a POSITIVE control. The `is None` guard does not go
    through the value-read projection and must keep proving, before AND after.
  * `1110_…_str_carrier_control.py` — the `str` carrier (`# pycsl-expected: FAIL`), which
    fails closed today for the WRONG REASON: a Why3 type accident, not a guard. This is the
    file that records why routes #50 and #51 probed this class and found nothing.
