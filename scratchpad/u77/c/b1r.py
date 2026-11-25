from dataclasses import dataclass
from typing import Any, Dict

PyVal = Any


@dataclass
class R:
    x: float


#@ assigns \nothing
def mk(r: R) -> Dict[str, PyVal]:
    return {"a": r.x}


#@ ensures \result == 1
#@ assigns \nothing
def g(r: R) -> int:
    d = mk(r)
    if d["a"] == d["a"]:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython g(R(nan)) =", g(R(float('nan'))), "claim 1")
