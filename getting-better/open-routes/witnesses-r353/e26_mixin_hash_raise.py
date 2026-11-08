# route #339: mixin defines __eq__ (so __hash__ None) on an opaque Enum; hash(x) admitted
from enum import Enum

class M:
    def __eq__(self, o: object) -> bool:
        return self is o

class C(M, Enum):
    A = 1

#@ no_exception \all
def f() -> int:
    x = C.A
    return hash(x)

if __name__ == "__main__":
    f()
