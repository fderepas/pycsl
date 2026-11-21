# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    v: int = 1


g = C()


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    g.v = 99
    return g.v
