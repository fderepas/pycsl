# OPEN ROUTE #260 — `except LookupError` DOES NOT CATCH A RAISED `KeyError`

**Status: OPEN (gen #36, 2026-10-17), Severity 1.** Red-team round 2; driver-reproduced at HEAD e152fa15 (rc=0).
`witnesses-r260/F3_keyerror_lookup.py`: `try: raise KeyError("k") / except LookupError: r = 7 / return r`,
`ensures \result == 0` PROVES vacuously (CPython 7). Emission `try raise KeyError with LookupError -> ... end`;
KeyError and LookupError are distinct Why3 exceptions and an undeclared `raises { KeyError }` makes the normal
path unreachable. Routes #174/#175 refuse broad/user classes but not builtin subclass pairs.
Repair: an `except C` must catch every modelled builtin subclass of C (KeyError/IndexError -> LookupError,
ZeroDivisionError -> ArithmeticError, ...) or be refused; an exception escaping a function that does not declare
it must not make the postcondition vacuous (it must be reported/refused).
