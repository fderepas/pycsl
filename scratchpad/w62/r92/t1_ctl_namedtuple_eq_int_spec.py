from typing import NamedTuple

class T(NamedTuple):
    x: int

#@ ensures \result == t
def dup(t: T) -> T:
    return T(t.x)
