r"""Test 4088 -- gen #37 route #316 (expected PASS): CONTROL: a method that only READS its list argument keeps the caller's knowledge (`ys[0] == 0`) and proves.
"""
# pycsl-expected: PASS
from typing import List
class P:
    def __init__(self) -> None:
        self.n = 0
    #@ requires len(xs) >= 1
    #@ assigns self.n
    def look(self, xs: List[int]) -> int:
        self.n = xs[0] + len(xs)
        return self.n

#@ ensures \result == 0
def f() -> int:
    ys = [0]
    p = P()
    p.look(ys)
    return ys[0]

if __name__ == "__main__":
    assert f() == 0, f()
