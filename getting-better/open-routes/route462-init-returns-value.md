# OPEN ROUTE #462 — `__init__` RETURNING A NON-None VALUE OWES NO TypeError AT CONSTRUCTION
**Status: REPAIRED (executor m1, driver run #3, 2026-10-29), Severity 1.** Red team 37 (2026-10-29, on 370db7dc2); driver repro (`scratchpad/rt37/driver-repro.txt`):
`e3/k014_init_returns_value.py` rc=0 Verification SUCCESS on 370db7dc2; CPython `TypeError: __init__() should return
None, not 'int'` when the claimed f constructs the class.
Witnesses `witnesses-r462/` (1): `e3_k014_init_returns_value.py`.

```
#462 `def __init__(self, ..): ...; return 1` -- a claimed caller `C(..)` PROVES; CPython raises TypeError.
  REPAIR (proposed): an `__init__` whose body can return a non-None value (any `return <expr>` that is not `None`) is
  refused (any claim in the file), or the construction call owes TypeError.
```

## REPAIR (executor m1, driver run #3, 2026-10-29, off b1611d192; annotations §7.230, translational §T.6.240)

In the same block as route #461 (any `no_exception` claim of a verified def in the file): an `__init__` of any class that
is `async`, or whose body (outside nested def / lambda / class bodies) holds a `yield` / `yield from` or a `return <expr>`
other than `return None`, is REFUSED (`PYCSL-R462-INIT-RETURNS-VALUE`). Witness 7150 (`e3_k014`: PROVED at base, REFUSED).
Control 7152 (a bare `return` and `return None` in `__init__`, claimed caller `C(n)`): PROVED at base and candidate.
Cost: 0 corpus / pyref / mirror files (byte-diff 0/0/0 in all three trees).

## RESIDUALS: refused even when the value-returning path is unreachable (over-refusal, measured 0).
