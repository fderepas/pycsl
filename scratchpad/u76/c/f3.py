from dataclasses import dataclass
from typing import Any, Dict

PyVal = Any


@dataclass
class R:
    x: float


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f(r: R) -> int:
    d: Dict[str, PyVal] = {"a": r.x}
    if isinstance(d.get("a"), float):
        return 1
    return 0


if __name__ == "__main__":
    print("CPython f(R(1.5)) =", f(R(1.5)))
