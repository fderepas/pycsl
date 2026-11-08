from typing import List
class P:
    def __init__(self) -> None:
        self.n = 0
    def bump(self, xs: List[int]) -> None:
        if len(xs) > 0:
            xs[0] = 5

#@ ensures \result == 0
def f() -> int:
    ys = [0]
    p = P()
    p.bump(ys)
    return ys[0]

if __name__ == "__main__":
    assert f() == 0, f()
