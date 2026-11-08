# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0


#@ requires a.tag == 1
#@ ensures \result == 2
def f(a: C) -> int:
    b: C = a
    b.tag = 2
    return a.tag
