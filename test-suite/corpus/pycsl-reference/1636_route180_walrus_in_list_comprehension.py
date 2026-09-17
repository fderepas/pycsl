r"""Test 1636 - ROUTE #180 (gen #29): `y = 0; xs = [(y := x) for x in [1, 2, 3]]; return y` PROVED `\result == 0` (CPython 3): PEP 572 binds a comprehension walrus in the enclosing function, and the comprehension is lowered as an opaque value. Now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    y = 0
    xs = [(y := x) for x in [1, 2, 3]]
    return y
