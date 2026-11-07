r"""Test 4515 -- gen #37 route #336 (expected FAIL): `xs: List[Fraction]`: element read as `int`, PROVED; CPython False. The element is erased; not provable.
"""
# pycsl-expected: FAIL
from typing import List
from fractions import Fraction
#@ requires len(xs) > 0
#@ ensures \result == True
def f(xs: List[Fraction]) -> bool:
    return xs[0] % 1 == 0
if __name__ == "__main__":
    assert f([Fraction(1, 2)]) == True
