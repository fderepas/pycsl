r"""Test 10515 -- run #9 u76, review rt84 F1 (u74 link-1 float-field PyVal carrier). `isinstance(<stored float field>, int)`
with r.x = 1.5: `cd <tree root> && python <this file>` prints "result 0", the claim is false (a non-integral
value is only ever `HFloat`, which `int` answers False; the claim stays unprovable).
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
    d: Dict[str, PyVal] = {"a": r.x}
    if isinstance(d.get("a"), int):
        return 1
    return 0


if __name__ == "__main__":
    print("result", f(R(1.5)))
