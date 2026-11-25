r"""Test 10511 -- run #9 u76, review rt84 F1 (u74 link-1 float-field PyVal carrier). Same carrier, `v != 0.5` after `v = d["a"]` with
r.x = 0.5: `cd <tree root> && python <this file>` prints "result 0", the claim is false (u74 head PROVED it).
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
    v = d["a"]
    if v != 0.5:
        return 1
    return 0


if __name__ == "__main__":
    print("result", f(R(0.5)))
