from typing import List
class P:
    def __init__(self) -> None:
        self.xs = [0, 0]
    def poke(self, a: List[int]) -> None:
        if len(a) > 0:
            a[0] = 5
    def bump(self) -> None:
        self.poke(self.xs)

#@ ensures \result == 0
def f() -> int:
    p = P()
    p.bump()
    return p.xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
