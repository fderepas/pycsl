from enum import IntEnum

class C(IntEnum):
    A = 1
    _C__B = 2

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C(2)
    return 0

if __name__ == "__main__":
    print(f())
