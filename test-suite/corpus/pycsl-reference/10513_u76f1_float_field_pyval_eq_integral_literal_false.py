r"""Test 10513 -- run #9 u76, review rt84 F1 (u74 link-1 float-field PyVal carrier). The float field against the integral
literal 2.0 with r.x = 2.0: `cd <tree root> && python <this file>` prints "result 0", the claim is false.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Any, Dict

PyVal = Any


@dataclass
class R:
    x: float


#@ ensures \result == 1
#@ assigns \nothing
def f(r: R) -> int:
    d: Dict[str, PyVal] = {"a": r.x}
    if d.get("a") == 2.0:
        return 0
    return 1


if __name__ == "__main__":
    print("result", f(R(2.0)))
