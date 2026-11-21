from enum import Enum
import functools

class C(Enum):
    A = 1
    B = functools.partial(int)

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C.B.value
    return 0

if __name__ == "__main__":
    print(f())
