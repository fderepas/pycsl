r"""Test 4483 -- gen #37 route #336 (expected FAIL): PEP 695 `type Num3 = float`: `x % 1 == 0` PROVED as an int; CPython False for 0.5. Resolved to `float`; not provable.
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
def f_type_stmt(x: Num3) -> bool:
    return x % 1 == 0

if __name__ == "__main__":
    assert f_type_stmt(*(0.5,)) == True, f_type_stmt(*(0.5,))
