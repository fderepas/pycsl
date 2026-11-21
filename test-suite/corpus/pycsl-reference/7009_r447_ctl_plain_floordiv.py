r"""Test 7009 -- route #447 (expected PASS): CONTROL -- the advice of PYCSL-R447-AUGASSIGN-DIVISION followed: `c = c // b` under `requires b > 0` proves `\result == a // b`; PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ requires b > 0
#@ ensures \result == a // b
#@ no_exception \all
def f(a: int, b: int) -> int:
    c = a
    c = c // b
    return c
