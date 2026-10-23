from dataclasses import dataclass


@dataclass
class P:
    x: float


#@ requires p.x == 0.1
#@ ensures \result == 0.3
#@ assigns \nothing
def f(p: P) -> float:
    return p.x + 0.2
