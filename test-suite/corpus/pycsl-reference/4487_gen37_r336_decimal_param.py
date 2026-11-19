r"""Test 4487 -- gen #37 route #336 (expected FAIL): `x: Decimal` lowered to `int`: `x % 1 == 0` PROVED; CPython False for Decimal('0.5'). Erased; not provable.
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
def f_decimal(x: Decimal) -> bool:
    return x % 1 == 0

if __name__ == "__main__":
    assert f_decimal(*(Decimal('0.5'),)) == True, f_decimal(*(Decimal('0.5'),))
