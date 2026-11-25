from dataclasses import dataclass
from typing import Any, Dict, Optional

PyVal = Any


@dataclass
class R:
    x: float


#@ ensures \result == 1
#@ assigns \nothing
def f(r: R) -> int:
    d: Dict[str, PyVal] = {"a": r.x}
    if d["a"] == d["a"]:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython f(R(float('nan'))) =", f(R(float('nan'))), "claim 1")
