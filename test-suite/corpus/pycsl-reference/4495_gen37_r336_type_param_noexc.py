r"""Test 4495 -- gen #37 route #336 (expected FAIL): `t: type`: `t - t == 0` PROVED under `no_exception \all` as an int; CPython TypeError. Erased: REFUSED (route #252).
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
#@ ensures \result == 0
def f_type_param(t: type) -> int:
    return t - t

if __name__ == "__main__":
    assert f_type_param(*(float,)) == 0, f_type_param(*(float,))
