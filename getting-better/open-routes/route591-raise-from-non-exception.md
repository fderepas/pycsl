# OPEN ROUTE #591 — raise E(...) from <non-exception value> (int / variable) PROVES WHILE CPYTHON RAISES TypeError
**Status: REPAIRED (driver run #6, executor u39, branch run6-u39; annotations §7.591). Was: OPEN, Severity 1, pre-existing (rt56 R56-C; proves on 822621340 and int55).** Witnesses witnesses-r591/ (ha1786, ha1787).

## REPAIR (driver run #6, executor u39, base c55a7b233 = run6-int56, branch run6-u39)

- RULE (annotations §7.591), same block as route #590: the `from` cause must be `None`, a name of an exception class
  (resolved as in #590), or the `except ... as` name of a handler ENCLOSING the raise and never rebound in it; anything
  else (a constant, a parameter, a local, an attribute, a pure-builtin call route #310 admits, ...) is REFUSED,
  `PYCSL-R591-RAISE-FROM-NON-EXCEPTION`. A cause that is a call of an exception class is route #310's refusal already.
  `from e` of the handler's own name passes this rule; every read of `e` is route #233's refusal today, so the control
  uses `from None` / `from ValueError`.
- WITNESSES / CONTROLS / INERTNESS: shared with routes #589 / #591 / #590, recorded once in `route589-raise-extra-ctor-args-dropped.md` (section WITNESSES, CONTROLS, INERTNESS).
