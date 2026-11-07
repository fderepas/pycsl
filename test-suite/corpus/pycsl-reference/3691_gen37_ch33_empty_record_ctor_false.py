r"""Test 3691 -- gen #37 ch33 (expected FAIL): false twin of 3690: the same field-less constructions under a WRONG postcondition (`\result == n`, CPython returns n + 1) must NOT prove.
"""
# pycsl-expected: FAIL
class Base:
    pass


class Marker(Base):
    pass


#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def f(n: int) -> int:
    m = Marker()
    k = Marker()
    return n + 1
