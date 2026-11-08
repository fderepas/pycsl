from enum import IntEnum

class C(IntEnum):
    A = 1
    B = 2

    def __eq__(self, other: object) -> bool:
        return False
    __hash__ = IntEnum.__hash__

#@ ensures \result == True
def f() -> bool:
    x = C.A
    return x == x

if __name__ == "__main__":
    assert f() == True
