r"""Test 4484 -- gen #37 route #336 (expected FAIL): `Num4 = TypeAliasType("Num4", float)`: `x % 1 == 0` PROVED as an int; CPython False for 0.5. Resolved to `float`; not provable.
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
def f_aliastype(x: Num4) -> bool:
    return x % 1 == 0

if __name__ == "__main__":
    assert f_aliastype(*(0.5,)) == True, f_aliastype(*(0.5,))
