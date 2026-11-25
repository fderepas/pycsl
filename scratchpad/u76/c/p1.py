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
    print("CPython f(R(1.5)) =", f(R(1.5)))
