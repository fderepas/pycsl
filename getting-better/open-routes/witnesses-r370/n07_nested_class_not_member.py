from enum import Enum

class C(Enum):
    A = 1
    class B:
        pass

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C.B.value
    return 0

if __name__ == "__main__":
    print(f())
