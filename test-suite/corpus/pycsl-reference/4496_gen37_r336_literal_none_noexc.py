r"""Test 4496 -- gen #37 route #336 (expected FAIL): `x: Literal[None]` (got `requires x = 0`): `x * 0 + 1 == 1` PROVED under `no_exception \all`; CPython TypeError. `Literal[None]` resolves to `None`, erased: REFUSED (route #252).
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

#@ no_exception \all
#@ ensures \result == 1
def f_literal_none(x: Literal[None]) -> int:
    return x * 0 + 1

if __name__ == "__main__":
    assert f_literal_none(*(None,)) == 1, f_literal_none(*(None,))
