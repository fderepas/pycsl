from typing import List
class P:
    def __init__(self, n: int) -> None:
        self.n = n
    #@ requires len(xs) >= 1
    def bump(self, xs: List[int]) -> None:
        xs[0] = 5

#@ ensures \result == 0
def f() -> int:
    ys = [0]
    p = P(0)
    p.bump(ys)
    return ys[0]

if __name__ == "__main__":
    assert f() == 0, f()
