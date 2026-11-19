# route #339: `class C(int, M, Enum)` with M.__lt__ -- int first, so int wins (control-ish), use __neg__? int has it. Use __bool__ via M before int
from enum import Enum

class M:
    def __sub__(self, o: object) -> int:
        return 1

class C(M, int, Enum):
    A = 1

#@ ensures \result == 0
def f() -> int:
    x = C.A
    return x - x

if __name__ == "__main__":
    assert f() == 0, f()
