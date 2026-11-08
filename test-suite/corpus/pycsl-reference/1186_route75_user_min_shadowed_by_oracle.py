"""1186 — ROUTE #75, THIRD CARRIER: a user-defined `min`.

`\result <= 1` proved while CPython answers 99.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 99
#@ assigns \nothing
def min(a: int, b: int) -> int:
    return 99

#@ ensures \result <= 1
#@ assigns \nothing
def f() -> int:
    return min(1, 2)
