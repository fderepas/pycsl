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
    v = d["a"]
    if v != 0.5:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython f(R(0.5)) =", f(R(0.5)))
