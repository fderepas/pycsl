r"""Test 7008 -- route #447 (expected PASS): CONTROL -- `c <<= b; c >>= b` under `requires b >= 0 and b < 64`: both obligations discharged; PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ requires b >= 0 and b < 64
#@ no_exception \all
def f(a: int, b: int) -> int:
    c = a
    c <<= b
    c >>= b
    return c
