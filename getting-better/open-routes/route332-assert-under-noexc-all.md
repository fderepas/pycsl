# OPEN ROUTE #332 — `assert c` IS ERASED EVEN UNDER `#@ no_exception \all` (CPython raises AssertionError)
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Found by the r327 executor; driver-reproduced on main (rc=0; CPython raises).
Witness `witnesses-r332/a01_assert_noexc_all.py`: `x = 1; assert x == 2; return 7` with `ensures \result == 7`, `no_exception \all` proves.
`assert` lowers to `()` by design (route #84, annotations §7.1), and AssertionError is outside the Phase-1 KNOWN_EXCEPTIONS set; but since
route #304 `\all` means ANY exception, so a reachable failing assert under `no_exception \all` is a false no-exception claim.
Repair: under `no_exception \all` (and under a named set that includes AssertionError or a base of it: Exception/BaseException), lower
`assert c[, msg]` to a proof obligation `assert { c }` (labelled `no_exception: AssertionError reachable`) — or refuse; elsewhere keep the
documented erasure (partial correctness; python -O). Check `assert` inside loops/branches/methods and with an effectful message.
