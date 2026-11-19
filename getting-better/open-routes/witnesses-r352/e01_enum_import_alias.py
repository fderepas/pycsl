# route #339: `from enum import Enum as E` -- base name `E` is not in the enum-base list
from enum import Enum as E

class C(E):
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C.A
    return x - x

if __name__ == "__main__":
    f()
