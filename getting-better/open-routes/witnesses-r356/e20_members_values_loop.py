# route #339: for m in C.__members__.values()
from enum import Enum

class C(Enum):
    A = 1

#@ no_exception \all
def f() -> int:
    n = 0
    for m in C.__members__.values():
        n = m - m
    return n

if __name__ == "__main__":
    f()
