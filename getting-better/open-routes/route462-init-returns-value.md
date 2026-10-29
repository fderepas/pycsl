# OPEN ROUTE #462 — `__init__` RETURNING A NON-None VALUE OWES NO TypeError AT CONSTRUCTION
**Status: OPEN, Severity 1.** Red team 37 (2026-10-29, on 370db7dc2); driver repro (`scratchpad/rt37/driver-repro.txt`):
`e3/k014_init_returns_value.py` rc=0 Verification SUCCESS on 370db7dc2; CPython `TypeError: __init__() should return
None, not 'int'` when the claimed f constructs the class.
Witnesses `witnesses-r462/` (1): `e3_k014_init_returns_value.py`.

```
#462 `def __init__(self, ..): ...; return 1` -- a claimed caller `C(..)` PROVES; CPython raises TypeError.
  REPAIR (proposed): an `__init__` whose body can return a non-None value (any `return <expr>` that is not `None`) is
  refused (any claim in the file), or the construction call owes TypeError.
```
