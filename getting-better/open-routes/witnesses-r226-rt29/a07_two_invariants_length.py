from typing import List

#@ class invariant self.x >= 0
#@ class invariant \length(self.xs) >= 0
class D:
    def __init__(self, x: int, xs: List[int]) -> None:
        self.x = x
        self.xs = xs

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    assert f(D(-1, [])) >= 0
