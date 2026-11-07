from enum import Enum
import types

class C(Enum):
    A = 1
    B = types.DynamicClassAttribute(lambda s: 1)

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C.B
    return 0

if __name__ == "__main__":
    print(f())
