r"""Test 4089 -- gen #37 route #316 (expected PASS): CONTROL: a method writing its argument havocs only THAT list; an unrelated list keeps its value and the caller proves.
"""
# pycsl-expected: PASS
from typing import List
class P:
    def __init__(self) -> None:
        self.n = 0
    def bump(self, xs: List[int]) -> None:
        if len(xs) > 0:
            xs[0] = 5

#@ ensures \result == 1
def f() -> int:
    ys = [0]
    zs = [1]
    p = P()
    p.bump(ys)
    return zs[0]

if __name__ == "__main__":
    assert f() == 1, f()
