r"""Test 2589 — route #258 (expected FAIL): a record field declared `Optional[Any]`; the claim that
`b.v is not None` never holds is FALSE (CPython: `f(Box(1))` is 6) and is not provable before or after
the repair (the field lowering never dropped the arm into a provable shape); kept as coverage of the
field seam of the `Any`-arm rule.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Box:
    v: Optional[Any]


#@ ensures \result == 5
#@ assigns \nothing
def f(b: Box) -> int:
    if b.v is not None:
        return 6
    return 5


if __name__ == "__main__":
    assert f(Box(1)) == 6
