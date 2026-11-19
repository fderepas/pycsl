r"""Test 4512 -- gen #37 route #336 (expected FAIL): `x: Optional[Fraction]`: the non-None union arm had an OPAQUE `int` payload, `x % 1 == 0` PROVED; CPython False for Fraction(1, 2). A non-record class arm now erases the annotation; not provable.
"""
# pycsl-expected: FAIL
from typing import Optional
from fractions import Fraction
#@ ensures \result == True
def f(x: Optional[Fraction]) -> bool:
    if x is None:
        return True
    return x % 1 == 0
if __name__ == "__main__":
    assert f(Fraction(1, 2)) == True
