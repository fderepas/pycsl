r"""Test 4076 -- gen #37 route #316 (expected FAIL): `self.poke(xs)` sibling write invisible to `run`; `\result == 0` PROVED (CPython 5). FAILS.
"""
# pycsl-expected: FAIL
from typing import List
class P:
    def __init__(self) -> None:
        self.n = 0
    #@ requires len(xs) >= 1
    def poke(self, xs: List[int]) -> None:
        xs[0] = 5
    #@ requires len(xs) >= 1
    #@ ensures \result == 0
    def run(self, xs: List[int]) -> int:
        xs[0] = 0
        self.poke(xs)
        return xs[0]

if __name__ == "__main__":
    assert P().run([0]) == 0
