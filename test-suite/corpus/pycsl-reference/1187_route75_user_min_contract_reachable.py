"""1187 — ROUTE #75 POSITIVE CONTROL for the `min` carrier.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 99
#@ assigns \nothing
def min(a: int, b: int) -> int:
    return 99

#@ ensures \result == 99
#@ assigns \nothing
def f() -> int:
    return min(1, 2)
