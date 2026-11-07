from enum import Enum

class C(Enum):
    A = 0
    __B = 1

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C(1)
    return 0

if __name__ == "__main__":
    print(f())
