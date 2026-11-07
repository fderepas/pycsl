# OPEN ROUTE #286 — ONE-ARGUMENT `.get` ON A NON-MAP hval RECEIVER UNDER `no_exception` (AttributeError dropped) — ON MAIN
**Status: REPAIRED (landed with the dict-value-wall stack 5e7f5fa2, 2026-10-22; driver-verified: 3289 FAILs on main) -- was OPEN on main / REPAIRED in the land27 stack (3cbcc895), gen #37, 2026-10-20, Severity 1.** Found by the driver's fresh
verification of land27: corpus witness 3289 (`3289_gen37_dvw_hval_doubled_get_nonmap_noexc_false_claim.py`, label FAIL) PROVES
rc=0 on main (base) and FAILS on land27. Same root as red-team round 7's R5 (receiver-form `(<hval> or {}).get`), but in the
one-argument read path that predates the ch26 seam: a non-HMap receiver answers a default where CPython raises AttributeError.
Repair (in land27): under `no_exception` the read asserts the receiver is a map (PyCSL-DVW-R5, also on one-arg `.get(k)`).
Closes when land27 lands on main (re-run 3289 on main then).
