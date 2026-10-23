r"""Test 1362 — ROUTE #130: `from ...r119_plainlib import inc` (+1) then `from ...r124_starlib import inc` (-1); the model kept the FIRST import and PROVED `inc(3) == 4` while CPython runs the second and returns 2. An imported name bound again in its scope is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r119_plainlib import inc
from multi_file_lib.r124_starlib import inc


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
