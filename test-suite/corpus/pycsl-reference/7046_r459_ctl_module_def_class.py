r"""Test 7046 -- route #459 (expected PASS): CONTROL -- an unconditional module `def g` and `class C` read by the claimed f; PROVED at base and candidate.
"""
# pycsl-expected: PASS
def g(x: int) -> int:
    return x + 1
class C:
    k = 1
#@ no_exception \all
def f(n: int) -> int:
    return g(n) + C.k
