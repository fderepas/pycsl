from typing import List
#@ requires len(xs) >= 1
#@ assigns xs[0]
#@ ensures xs[0] == 5
def g(xs: List[int]) -> None:
    xs[0] = 5

class P:
    def __init__(self, n: int) -> None:
        self.n = n
    #@ requires len(xs) >= 1
    def go(self, xs: List[int]) -> None:
        g(xs)

#@ ensures \result == 0
def f() -> int:
    ys = [0]
    p = P(0)
    p.go(ys)
    return ys[0]

if __name__ == "__main__":
    assert f() == 0, f()
