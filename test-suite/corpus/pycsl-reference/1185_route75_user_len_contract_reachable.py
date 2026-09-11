"""1185 — ROUTE #75 POSITIVE CONTROL for the `len` carrier.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == -5
#@ assigns \nothing
def len(x: str) -> int:
    return -5

#@ ensures \result == -5
#@ assigns \nothing
def f() -> int:
    return len("ab")
