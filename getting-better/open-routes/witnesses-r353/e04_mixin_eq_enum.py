# route #339: opaque Enum, user __eq__ in a non-enum mixin -> `==` admitted with Why3 `=`
from enum import Enum

class M:
    def __eq__(self, o: object) -> bool:
        return False
    __hash__ = object.__hash__

class C(M, Enum):
    A = 1
    B = 2

#@ ensures \result == True
def f() -> bool:
    x = C.A
    return x == x

if __name__ == "__main__":
    assert f() == True, f()
