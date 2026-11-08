from enum import Enum

class C(Enum):
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == False
def f() -> bool:
    x = C.A
    return x < x

if __name__ == "__main__":
    assert f() == False
