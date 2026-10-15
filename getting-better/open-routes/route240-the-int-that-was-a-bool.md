# OPEN ROUTE #240 — `isinstance(<int>, bool)` IS DECIDED TRUE

**Status: OPEN (gen #36, 2026-10-15), Severity 1.** Recorded as a residual by the #239 repair executor;
driver-reproduced at HEAD ab2c2d4f (rc=0 "Verification SUCCESS"; CPython `f(5)` = 0).

## Witness
`witnesses-r240/isinstance_int_is_bool.py`: `def f(x: int)`: `if isinstance(x, bool): return 1` / `return 0`,
`ensures \result == 1` PROVES.

## Mechanism (per the #239 executor)
`_tag_of_value` / isinstance lowering collapses `bool` onto `tag_int` (bool is a subclass of int, so
`isinstance(True, int)` is True — but the converse is false: an int is not a bool). A typed-`int` subject
therefore decides `isinstance(x, bool)` TRUE.

## Repair direction
`isinstance(<int-typed>, bool)` must be opaque (or decided by a modelled bool flag), never true;
`isinstance(<bool-typed>, int)` stays true. Check the hval `HInt` arm (already opaque after #237) and the
`True`/`1` typeof_op collision noted in the #239 doc.
