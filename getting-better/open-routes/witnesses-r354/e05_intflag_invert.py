# route #339: IntFlag is "transparent" but Flag overrides __invert__ (~A == B, not -2)
from enum import IntFlag

class F(IntFlag):
    A = 1
    B = 2

#@ ensures \result == -1
def f() -> int:
    x = F.A
    return x + ~x

if __name__ == "__main__":
    assert f() == -1, f()
