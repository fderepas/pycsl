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
    if d.get("a") == True:
        return 0
    return 1


if __name__ == "__main__":
    print("CPython f(R(1.0)) =", f(R(1.0)))
