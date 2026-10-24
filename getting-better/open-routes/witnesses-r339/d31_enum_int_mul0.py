from enum import Enum

class C(Enum):
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C.A
    return x * 0

if __name__ == "__main__":
    assert f() == 0
