r"""Test 7654 -- route #482 CONTROL (expected PASS: PROVED at base and candidate): a `\trusted` def with no `assigns` reads its record parameter's list field into a local by a plain `=` (an alias the inference follows) and only reads it; the caller keeps `o.v`.
"""
# pycsl-expected: PASS
from typing import List


class C:
    def __init__(self) -> None:
        self.v = 0
        self.xs: List[int] = [0]


#@ \trusted
def k(o: C) -> int:
    ys = o.xs
    if len(ys) > 0 and ys[0] > 5:
        return 1
    return 0


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    k(o)
    return o.v


if __name__ == "__main__":
    print("result", f(0), "expected 0")
