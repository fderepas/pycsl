r"""Test 1534 - ROUTE #158 (gen #29): `all(x > 0 for x in [])` - the empty literal lowers to the placeholder `(Array.make 1024 0)` and the fold quantified over 1024 zeros, so `\result != 1` PROVED; CPython 1 (`all` of nothing is True). The fold now declines when the Why3 length is not the list's.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    return 1 if all(x > 0 for x in []) else 0

