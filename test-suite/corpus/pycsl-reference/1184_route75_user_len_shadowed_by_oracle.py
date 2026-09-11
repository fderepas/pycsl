"""1184 — ROUTE #75, SECOND CARRIER: a user-defined `len`.

`\result >= 0` proved while CPython answers -5. Kept separate from 1182 because the carriers
are NOT uniform -- `bool`, `repr` and `hash` shadowed the same way do not prove -- so a guard
written as a list of names would be stepped around by the next name in the table.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == -5
#@ assigns \nothing
def len(x: str) -> int:
    return -5

#@ ensures \result >= 0
#@ assigns \nothing
def f() -> int:
    return len("ab")
