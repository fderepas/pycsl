r"""Test 1364 — ROUTE #130 (compound arm): `if FLAG == 1: from starlib import inc / else: from plainlib import inc` with `FLAG = 0`; the model kept the textually FIRST import (-1) and PROVED `inc(3) == 2` while CPython takes the `else` (+1) and returns 4.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
FLAG = 0
if FLAG == 1:
    from multi_file_lib.r124_starlib import inc
else:
    from multi_file_lib.r119_plainlib import inc


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return inc(3)
