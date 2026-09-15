r"""Test 1321 — ROUTE #118 negative: a module-level rebinding `inc = dec` was IGNORED — every
later `inc(3)` was modelled against the original `def inc`, so `\result == 4` PROVED while
CPython returns 2. The front end now REFUSES a module that rebinds a def/class name after
defining it (PYCSL-IR-FUNCTION-NAME-REBOUND).
"""
# pycsl-expected: FAIL
#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1


#@ ensures \result == y - 1
#@ assigns \nothing
def dec(y: int) -> int:
    return y - 1


inc = dec


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
