# route #339: mixin __lt__ on an IntEnum subclass of a file enum base (B(IntEnum) members-free)
from enum import IntEnum

class M:
    def __lt__(self, o: object) -> bool:
        return True

class Base(IntEnum):
    pass

class C(M, Base):
    A = 1

#@ ensures \result == False
def f() -> bool:
    x = C.A
    return x < x

if __name__ == "__main__":
    assert f() == False, f()
