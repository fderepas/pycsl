# OPEN ROUTE #460 — A CALLER'S CLAIM DOES NOT REACH ITS CALLEES' MODULE 6 OBLIGATIONS / #161 ADMISSION
**Status: OPEN, Severity 1.** Measured by executor r1 (driver run #3, 2026-10-29, routes #444-#458 increment 2) and
driver-reproduced: `scratchpad/rt36/r460_factorial_unclaimed_callee.py` PROVES rc=0 (Verification SUCCESS) on main
8fe7204c3 AND on the post-#444-#459 candidate, while CPython raises `ValueError: factorial() not defined for negative
values` (`scratchpad/rt36/../` driver repro: `/tmp/.../scratchpad/rp36/r460.txt`, 2026-10-29T07:06Z).
Witnesses `witnesses-r460/` (1): `r460_factorial_unclaimed_callee.py`.

```
#460 CLAIM REACH: `#@ no_exception \all` on f; f calls an UN-claimed g; g's Module 6 obligations (#160 / #434 / #436 /
     #437 ...) and route #161's admission are judged under g's OWN (empty) claim, so g's exceptions are owed nowhere.
  def g(n: int) -> int: return math.factorial(n)        # no claim
  #@ no_exception \all
  def f(n: int) -> int: return g(n)                     # PROVED; f(-1) -> CPython ValueError
  Partial closures already landed: route #178's callee summary (#430 hashing, #434-#436 sites), r1's `_rc444` claim
  reach for the #444-#458 opaque-fallback rules and #441's builtin-function rows (`_xf440`). r1 measured that extending
  the WHOLE #432 / #440 claim to callees refuses 10 accepted corpus files (`super()` receivers in reached constructors,
  `list.pop`), so it was not landed.
  REPAIR (proposed, structural): compute the reached-claim set of every function ONCE (the union of its callers'
  claims, through the call graph, `_rc444`) and make every claim-gated check -- Module 6 obligation emission
  (`_current_no_exception_all`), #161 admission, #432 / #440 receiver rules -- read the reached claim, not the
  function's own; measure the corpus cost per rule and narrow the 10 known over-refusals (constructor super() receivers,
  list.pop) with explicit rows.
```
