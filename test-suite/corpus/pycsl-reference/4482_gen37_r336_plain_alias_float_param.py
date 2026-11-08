r"""Test 4482 -- gen #37 route #336 (expected FAIL): plain alias `Num2 = float`: `x % 1 == 0` PROVED as an int; CPython False for 0.5. Resolved to `float`; not provable.
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
def f_plain_alias(x: Num2) -> bool:
    return x % 1 == 0

if __name__ == "__main__":
    assert f_plain_alias(*(0.5,)) == True, f_plain_alias(*(0.5,))
