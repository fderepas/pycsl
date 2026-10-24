from enum import Enum

class C(Enum):
    A = 2
    B = 3

#@ no_exception \all
#@ ensures \result >= 0
def f() -> int:
    x = C.A
    return x * x

if __name__ == "__main__":
    assert f() >= 0
