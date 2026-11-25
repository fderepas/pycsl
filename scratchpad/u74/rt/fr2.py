from dataclasses import dataclass
from typing import Dict


@dataclass
class R:
    a: int
    b: int


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(r: R) -> Dict[str, PyVal]:
    r.b = 5
    return {"a": r.a}


#@ requires True
#@ ensures \result == 0
def g() -> int:
    r = R(1, 0)
    f(r)
    return r.b


if __name__ == "__main__":
    print("CPython g() =", g())
