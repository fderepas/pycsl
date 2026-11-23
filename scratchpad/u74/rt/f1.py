from dataclasses import dataclass


@dataclass
class R:
    x: float


#@ requires True
#@ ensures \result == 1
def g(y: float) -> int:
    if isinstance(y, float):
        return 1
    return 0


#@ requires True
#@ ensures \result == 1
def h() -> int:
    return g(0)


#@ requires True
#@ ensures True
def k() -> float:
    r = R(0)
    return r.x
