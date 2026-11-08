r"""Test 1384 — ROUTE #136: a dynamic `exec` rebinding an IMPORTED name. `inc(3)` PROVED `\result == 4` while CPython runs `dec` and returns 2.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r119_plainlib import inc
from multi_file_lib.r119_plainlib import dec

exec("in" + "c = dec")


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
