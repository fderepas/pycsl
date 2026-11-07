# route #339: IntFlag(boundary=STRICT) `~x` is fine but `F(8)` raises; and `x ^ 8` raises
from enum import IntFlag, STRICT

class F(IntFlag, boundary=STRICT):
    A = 1
    B = 2

#@ no_exception \all
def f() -> int:
    x = F.A
    y = x ^ 8
    return 0

if __name__ == "__main__":
    f()
