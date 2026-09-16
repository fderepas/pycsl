r"""Test 1403 — ROUTE #137: the same dict reached through the interpreter frame — `inspect.currentframe().f_globals["N"] = 5`. PROVED `f() == 3`; CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import inspect

N = 3
inspect.currentframe().f_globals["N"] = 5


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
