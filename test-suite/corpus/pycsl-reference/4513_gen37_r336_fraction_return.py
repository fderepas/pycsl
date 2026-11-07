r"""Test 4513 -- gen #37 route #336 (expected FAIL): `-> Fraction` lowered to an `int` result: `ensures \result % 1 == 0` PROVED for `return x`; CPython False. The result is erased; not provable.
"""
# pycsl-expected: FAIL
from fractions import Fraction
#@ ensures \result % 1 == 0
def f(x: Fraction) -> Fraction:
    return x
if __name__ == "__main__":
    assert f(Fraction(1, 2)) % 1 == 0
