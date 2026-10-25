from enum import Enum

class C(Enum):
    _C__B = 2
    A = 1

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C._C__B
    y = x.value
    return 0

if __name__ == "__main__":
    print(f())
