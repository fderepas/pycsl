from enum import IntEnum

class C(IntEnum):
    A = 1
    B = 2

    def __lt__(self, other: object) -> bool:
        return True

#@ ensures \result == False
def f() -> bool:
    x = C.A
    return x < x

if __name__ == "__main__":
    assert f() == False
