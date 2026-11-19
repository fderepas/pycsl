r"""Test 4491 -- gen #37 route #336 (expected FAIL): `x: S` with `S: TypeAlias = str`: `x - x == 0` PROVED under `no_exception \all` as an int; CPython TypeError. Resolved to `str`; not provable.
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
def f_alias_str(x: S) -> int:
    return x - x

if __name__ == "__main__":
    assert f_alias_str(*('a',)) == 0, f_alias_str(*('a',))
