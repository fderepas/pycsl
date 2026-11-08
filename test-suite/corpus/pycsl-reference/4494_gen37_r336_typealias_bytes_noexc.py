r"""Test 4494 -- gen #37 route #336 (expected FAIL): `x: B` with `B: TypeAlias = bytes`: `x * 0 + 1 == 1` PROVED under `no_exception \all`; CPython TypeError. Resolved to `bytes` (identical to `x: bytes`); not provable.
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
def f_alias_bytes(x: B) -> int:
    return x * 0 + 1

if __name__ == "__main__":
    assert f_alias_bytes(*(b'a',)) == 1, f_alias_bytes(*(b'a',))
