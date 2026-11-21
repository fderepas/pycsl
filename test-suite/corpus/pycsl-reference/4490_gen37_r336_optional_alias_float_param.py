r"""Test 4490 -- gen #37 route #336 (expected FAIL): `x: Optional[Num]` (alias of float): the union arm was `int`, `x % 1 == 0` PROVED; CPython False for 0.5. The arm resolves to `real`; not provable.
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
def f_opt_alias(x: Optional[Num]) -> bool:
    if x is None:
        return True
    return x % 1 == 0

if __name__ == "__main__":
    assert f_opt_alias(*(0.5,)) == True, f_opt_alias(*(0.5,))
