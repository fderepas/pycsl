r"""Test 4486 -- gen #37 route #336 (expected FAIL): `x: Fraction` (an unrecognised import) lowered to `int`: `x % 1 == 0` PROVED; CPython False for Fraction(1, 2). The parameter is now ERASED (route #249 arbitrary object); not provable.
"""
# pycsl-expected: FAIL
from typing import Literal, Sequence, TypeAlias, Annotated, Optional, SupportsFloat, TypeAliasType
from fractions import Fraction
from decimal import Decimal
from numbers import Real

Num: TypeAlias = float
Num2 = float
type Num3 = float
Num4 = TypeAliasType("Num4", float)
S: TypeAlias = str
N: TypeAlias = None
B: TypeAlias = bytes

#@ ensures \result == True
def f_fraction(x: Fraction) -> bool:
    return x % 1 == 0

if __name__ == "__main__":
    assert f_fraction(*(Fraction(1, 2),)) == True, f_fraction(*(Fraction(1, 2),))
