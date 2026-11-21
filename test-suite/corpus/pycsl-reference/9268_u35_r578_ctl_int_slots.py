r"""Test 9268 -- route #578 CONTROL (expected PASS at base and HEAD): the `int` slots of a call-bound tuple whose OTHER slot is
`Any` keep their int laws: `t[0] < k`, `t[0] + 1`, `t[0] & 1` of `t = g(k)` (`g -> Tuple[int, Any]`), the same through a method
`self.h(k)`, and an unpacked `int` slot `a, _ = g(k)`; bitwise / power ops on `int` parameters carry no erased-operand obligation.
"""
# pycsl-expected: PASS
from typing import Any, Tuple


def g(k: int) -> Tuple[int, Any]:
    return (1, None)


#@ no_exception \all
def f1(k: int) -> int:
    t = g(k)
    return 1 if t[0] < k and t[0] + 1 > 0 and (t[0] & 1) == 1 else 0


#@ no_exception \all
def f2(k: int) -> int:
    a, b = g(k)
    return 1 if a < k else 0


#@ requires 0 <= k and k <= 10
#@ no_exception \all
def f3(k: int) -> int:
    return (k & 1) + (k | 2) + (k ^ 3) + k ** 2 + (k << 1) + (k >> 1)


class C:
    def __init__(self) -> None:
        self.z: int = 0

    def h(self, k: int) -> Tuple[int, Any]:
        return (2, None)

    #@ no_exception \all
    def f4(self, k: int) -> int:
        t = self.h(k)
        return 1 if t[0] < k else 0


if __name__ == "__main__":
    print(f1(3), f2(3), f3(3), C().f4(3))
