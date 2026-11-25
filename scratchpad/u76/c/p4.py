from dataclasses import dataclass
from typing import Any, Dict

PyVal = Any


@dataclass
class R:
    x: float


#@ requires r.x == 2.0
#@ ensures \result == 0
#@ assigns \nothing
def f(r: R) -> int:
    d: Dict[str, PyVal] = {"a": r.x}
    if d.get("a") == 2:
        return 0
    return 1


if __name__ == "__main__":
    print("CPython f(R(2.0)) =", f(R(2.0)))
