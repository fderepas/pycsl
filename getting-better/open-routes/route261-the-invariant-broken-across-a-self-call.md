# OPEN ROUTE #261 — A SELF-CALL WHILE THE CLASS INVARIANT IS BROKEN ASSUMES IT HOLDS

**Status: REPAIRED (gen #36, 2026-10-17; opened the same day), Severity 1.** Red-team round 2; driver-reproduced at HEAD e152fa15 (rc=0, CPython -1).
`witnesses-r261/F4_classinv_selfcall.py`: invariant `self.n >= 0`; method `a`: `self.n = -1; r = self.peek();
self.n = 0; return r` with `ensures \result >= 0` PROVES. The self-call lowers to a receiver-less
`val self_peek_0 () : int ensures { result >= 0 }`, so Why3 never re-checks the type invariant at the call; the
module-level `c.peek()` form (`(c_peek_0 c)`) correctly fails ("type invariant").
Repair: a self-call must check the class invariant at the call (pass the receiver / assert the invariant) or the
callee's postcondition must not rely on it.

## Repair (gen #36, 2026-10-17)
Route #165's receiver pass in `_handle_dotted_call` (mirror twin `\trusted`) now covers `self.<m>(...)`:
inside a method of a class with `#@ class invariant`s, the generic abstract op takes `(self: <cls>)` and is
applied to `self`, so Why3 checks the type invariant at the call (the `c.m()` form already did). Concrete
sibling applications and the field-spec path already passed `self`. Witnesses 2735 (F4) and 2736 (with an
argument + callee `requires`) PROVED -> FAIL ("type invariant" at the call); control 2737 (invariant intact)
keeps PASS. `super().m()`, `s = self; s.m()` and `c.m()` on a parameter were probed: all fail closed.
Blast radius: corpus 1 MOVED (0453, inherited `generic_visit` under a base-class invariant; still PROVES);
mirror 2 MOVED (`frontend/Module2_Parser`: 9 calls of `self._err`; `frontend/pure_ast`: 23 calls of
`self.error`/`self.unsupported`, all `-> NoReturn`), type-only clean; Why3 generates NO type-invariant goal
at any changed line (self unmodified there) and every goal at those lines is Valid; whole-file proofs OWED.
