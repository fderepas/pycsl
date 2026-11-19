from typing import List
class P:
    @staticmethod
    def bump(xs: List[int]) -> None:
        if len(xs) > 0:
            xs[0] = 5

#@ ensures \result == 0
def f() -> int:
    ys = [0]
    P.bump(ys)
    return ys[0]

if __name__ == "__main__":
    assert f() == 0, f()
