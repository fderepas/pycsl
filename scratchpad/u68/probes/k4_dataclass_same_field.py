from dataclasses import dataclass


@dataclass
class Ab:
    x: int


@dataclass
class AB:
    x: int


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    a = AB(1)
    return a.x
