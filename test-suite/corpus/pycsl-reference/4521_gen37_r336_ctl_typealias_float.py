r"""Test 4521 -- gen #37 route #336 (expected PASS): CONTROL: `x: Num` (`Num: TypeAlias = float`), `requires x > 0.0` / `ensures \result > 0.0` for `return x` PROVES (FAILED before: the int-typed alias clashed with the real literal).
"""
# pycsl-expected: PASS
from typing import TypeAlias
Num: TypeAlias = float

#@ requires x > 0.0
#@ ensures \result > 0.0
def pos(x: Num) -> float:
    return x

if __name__ == "__main__":
    assert pos(0.5) > 0.0
