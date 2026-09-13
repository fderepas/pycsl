from typing import NamedTuple

class C:
    v: int
    def __init__(self, v: int) -> None:
        self.v = v

class T(NamedTuple):
    c: C

#@ ensures \result != t
def dup(t: T) -> T:
    return T(C(t.c.v))
