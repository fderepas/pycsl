# OPEN ROUTE #246 — ON AN `Any` PARAMETER, `isinstance(x, int)` CANNOT TELL `1` FROM `1.0`

**Status: OPEN (gen #36, 2026-10-16), Severity 1.** Residual of the #245 repair; driver-reproduced at
8260571f (both rc=0) and present at HEAD dfaaeb82.

## Witnesses (`witnesses-r245/`)
- `any_int_vs_float_in_contract.py`: `requires x == y`, `ensures isinstance(x, int) == isinstance(y, int)` PROVES.
- `any_int_vs_float_program_side.py`: `if isinstance(x, int): if not isinstance(y, int): return 0` with
  `ensures \result == 1` PROVES. CPython `f(1, 1.0)` breaks both. float/set analogues also prove.

## Mechanism
An `Any` parameter is stored as an int; #239 lowered `isinstance(x, T)` to `subtag (typeof_op x) T`, a
function of the STORED integer, so Python values of different types that compare equal (1 / 1.0,
{1} / frozenset({1})) get the same answer in contracts and program bodies.

## Repair direction
Fail-closed for classes with cross-type `==` (int/float/bool/complex, set/frozenset, bytes/bytearray,
user classes): a program-side test is a fresh opaque per evaluation and a contract-side test is refused —
while keeping #239's `requires isinstance(x, int)` -> body link (control 2212) where it is sound (e.g. tie
the type tag to the PARAMETER rather than to its value, or keep the link only for classes whose `==` never
crosses types).
