# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a = C()
    a.tag = 1
    b = a
    b.tag = 2
    return a.tag
