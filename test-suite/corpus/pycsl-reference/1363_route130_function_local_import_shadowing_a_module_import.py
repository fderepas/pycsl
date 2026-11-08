r"""Test 1363 — ROUTE #130 (local arm): the module imports `inc` (+1) and `f` imports another `inc` (-1) locally; the model resolved `f`'s call to the module import and PROVED `\result == 4` while CPython returns 2. A function-local import of a name the module binds differently is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r119_plainlib import inc


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    from multi_file_lib.r124_starlib import inc
    return inc(3)
