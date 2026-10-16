# OPEN ROUTE #256 — TWO LIST FIELDS OF ONE RECORD MAY HOLD THE SAME LIST

**Status: OPEN (gen #36, 2026-10-16), Severity 1 (weaker: the alias is built in unverified code).** Red-team
finding; driver-reproduced at HEAD fa283db6 (rc=0; CPython 7).

## Witness
`witnesses-r256/p34_two_list_fields_store.py`: `T.poke` (`assigns self.xs`) does `self.xs[0] = 7`, returns
`self.ys[0]` under `requires self.ys[0] == 0`; `ensures \result == 0` proves. CPython: `L = [0]; T(L, L).poke()` = 7.

## Mechanism
Why3 regions assume distinct record fields never alias (emitted frame `ensures { self.ys = old self.ys }`). A
verified caller that builds the alias fails closed (R167), so the hole needs an unverified constructor call.

## Repair direction
Either surface "distinct mutable fields of a record are disjoint objects" as a DECLARED model assumption
(soundness report, like FLOAT-FINITE/BUILTIN-EXACT — the ownership doc's rule R1 is the existing statement),
or refuse a method that mutates one array field and reads another of the same type without a separation
precondition. Decide with the blast radius measured.
