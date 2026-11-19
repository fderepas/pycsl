r"""Test 4480 -- gen #37 route #336 (expected FAIL): `Num: TypeAlias = float` parameter (red-team a04): lowered `x: int`, so `x % 1 == 0` PROVED; CPython False for 0.5. The alias now resolves to `float` (emission identical to `x: float`) and the claim is not provable.
"""
# pycsl-expected: FAIL
from typing import TypeAlias
Num: TypeAlias = float

#@ ensures \result == True
def f(x: Num) -> bool:
    return x % 1 == 0

if __name__ == "__main__":
    assert f(0.5) == True, f(0.5)
