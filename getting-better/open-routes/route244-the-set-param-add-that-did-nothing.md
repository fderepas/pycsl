# OPEN ROUTE #244 — `s.add(x)` ON A SET PARAMETER IS A NO-OP UNDER `@mutable_state`

**Status: OPEN (gen #36, 2026-10-16), Severity 1.** Found by the ch16 chain agent; driver-reproduced at HEAD
4b894167 (rc=0 "Verification SUCCESS"; CPython `C().c()` = True, claim `\result == False`).

## Witness
`witnesses-r244/set_param_add_is_noop.py`: `m(self, s: Set[int])` does `s.add(1)` under `assigns \nothing`;
caller `c()`: `s = set(); s.add(2); self.m(s); return 1 in s` proves `\result == False`.

## Mechanism
`statements.py`'s "sound no-op" arm lowers an in-place mutator on a set PARAMETER (inside a `@mutable_state`
class) to nothing; the callee's frame says `\nothing`, so the caller keeps its pre-call value of `s`.

## Repair direction
Refuse an in-place mutation of a parameter's collection (caller-visible side effect) unless the frame can
express it (a by-reference carrier / caller-visible `writes`); never a silent no-op.
