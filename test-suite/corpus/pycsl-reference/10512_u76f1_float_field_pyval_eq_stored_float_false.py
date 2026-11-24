r"""Test 10512 -- run #9 u76, review rt84 F1 (u74 link-1 float-field PyVal carrier). The float field against a float literal
stored in the SAME dict (`hval_eq` of the two values, not the literal unfolding): `cd <tree root> && python
<this file>` prints "result 0", the claim is false.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Any, Dict

PyVal = Any


@dataclass
class R:
    x: float


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f(r: R) -> int:
    d: Dict[str, PyVal] = {"a": r.x, "b": 1.5}
    if d["a"] == d["b"]:
        return 0
    return 1


if __name__ == "__main__":
    print("result", f(R(1.5)))
