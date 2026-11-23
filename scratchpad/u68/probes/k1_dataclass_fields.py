from dataclasses import dataclass


@dataclass
class Ab:
    x: int


@dataclass
class AB:
    y: int


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    a = Ab(1)
    return a.x
