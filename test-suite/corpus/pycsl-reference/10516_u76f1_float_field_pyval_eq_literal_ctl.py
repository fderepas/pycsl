r"""Test 10516 -- run #9 u76, review rt84 F1 (u74 link-1 float-field PyVal carrier). Control: with `requires r.x == 1.5` the stored
field equals the literal 1.5 (`cd <tree root> && python <this file>` prints "result 0"): the faithful carrier
PROVES the true claim (u74 head could not: its erased carrier answered `false`).
"""
# pycsl-expected: PASS
from dataclasses import dataclass
from typing import Any, Dict

PyVal = Any


@dataclass
class R:
    x: float


#@ requires r.x == 1.5
#@ ensures \result == 0
#@ assigns \nothing
def f(r: R) -> int:
    d: Dict[str, PyVal] = {"a": r.x}
    if d.get("a") == 1.5:
        return 0
    return 1


if __name__ == "__main__":
    print("result", f(R(1.5)))
