r"""Test 1387 — ROUTE #136: a bare `exec` inside a function assigns into the discarded locals snapshot, but one given an EXPLICIT mapping writes the module globals. `exec(code, globals())` then `return N` PROVED `\result == 3` under the default hoare model while CPython (with code `"N = 5"`) returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f(code: str) -> int:
    exec(code, globals())
    return N
