r"""Test 4493 -- gen #37 route #336 (expected FAIL): `x: N` with `N: TypeAlias = None`: `x * 0 + 1 == 1` PROVED under `no_exception \all`; CPython TypeError. A `None`-annotated parameter is erased: REFUSED (route #252 erased value into an `-> int` slot).
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
def f_alias_none(x: N) -> int:
    return x * 0 + 1

if __name__ == "__main__":
    assert f_alias_none(*(None,)) == 1, f_alias_none(*(None,))
