# OPEN ROUTE #261 — A SELF-CALL WHILE THE CLASS INVARIANT IS BROKEN ASSUMES IT HOLDS

**Status: OPEN (gen #36, 2026-10-17), Severity 1.** Red-team round 2; driver-reproduced at HEAD e152fa15 (rc=0, CPython -1).
`witnesses-r261/F4_classinv_selfcall.py`: invariant `self.n >= 0`; method `a`: `self.n = -1; r = self.peek();
self.n = 0; return r` with `ensures \result >= 0` PROVES. The self-call lowers to a receiver-less
`val self_peek_0 () : int ensures { result >= 0 }`, so Why3 never re-checks the type invariant at the call; the
module-level `c.peek()` form (`(c_peek_0 c)`) correctly fails ("type invariant").
Repair: a self-call must check the class invariant at the call (pass the receiver / assert the invariant) or the
callee's postcondition must not rely on it.
