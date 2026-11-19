r"""Test 1637 - ROUTE #180 (gen #29): `last = 0; t = sum((last := x) for x in [1, 2, 3]); return last` PROVED `\result == 0` (CPython 3).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    last = 0
    t = sum((last := x) for x in [1, 2, 3])
    return last
