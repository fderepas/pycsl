r"""Test 1535 - ROUTE #158 (gen #29): `any(x == 0 for x in [])` folded over the placeholder zeros and `\result != 0` PROVED; CPython 0.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    return 1 if any(x == 0 for x in []) else 0

