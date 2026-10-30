r"""Test 7650 -- route #482 CONTROL (expected PASS: PROVED at base and candidate): a `\trusted` def with no `assigns` only READS its record parameter (`o.v` into arithmetic and a test), so its inferred frame is exact and the caller keeps `o.v`.
"""
# pycsl-expected: PASS
from typing import List


class C:
    def __init__(self) -> None:
        self.v = 0


#@ \trusted
def k(o: C) -> int:
    if o.v > 3:
        return o.v + 1
    return 0


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    k(o)
    return o.v


if __name__ == "__main__":
    print("result", f(0), "expected 0")
