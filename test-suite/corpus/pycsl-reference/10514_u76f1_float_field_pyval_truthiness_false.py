r"""Test 10514 -- run #9 u76, review rt84 F1 (u74 link-1 float-field PyVal carrier). Truthiness of the stored float field with
r.x = 1.5: `cd <tree root> && python <this file>` prints "result 0", the claim is false.
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
    if d.get("a"):
        return 0
    return 1


if __name__ == "__main__":
    print("result", f(R(1.5)))
