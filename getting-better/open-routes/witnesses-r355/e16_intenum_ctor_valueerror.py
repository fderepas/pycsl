# route #339: C(99) on a transparent IntEnum raises ValueError
from enum import IntEnum

class C(IntEnum):
    A = 1

#@ no_exception \all
def f() -> int:
    x = C(99)
    return 0

if __name__ == "__main__":
    f()
