# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a = C()
    a.tag = 5
    b = C()
    b.tag = 5
    if a == b:
        return 1
    return 0
