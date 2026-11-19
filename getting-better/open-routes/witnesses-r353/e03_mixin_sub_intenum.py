# route #339: dunder supplied by a NON-enum mixin base; IntEnum judged transparent
from enum import IntEnum

class M:
    def __sub__(self, o: object) -> int:
        return 1

class C(M, IntEnum):
    A = 1
    B = 2

#@ ensures \result == 0
def f() -> int:
    x = C.A
    return x - x

if __name__ == "__main__":
    assert f() == 0, f()
