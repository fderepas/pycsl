# OPEN ROUTE #390 — `**mapping` INTO BUILTINS IS DROPPED
**Status: OPEN, Severity 1.** Red-team round 30 (2026-10-25, probes around #373-#380 and route #226 increment 2c); driver-reproduced on main a064a298f (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt30/driver-repro.txt`).
Witnesses `witnesses-r390/`: `i13_sorted_kwargs_reverse.py`, `n08_sum_kwargs_start.py`.

`sorted(xs, **{"reverse": True})` modelled ascending; `sum([1, 2], **{"start": 10})` modelled 3 (#379 residual 2). CPython `[2, 1]` / 13.

Repair: Extend PYCSL-R379-STARRED-CALL-ARGUMENT to builtin and library calls (measure the blast radius).
