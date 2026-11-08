from typing import Any


class Box:
    def __init__(self, v: int, w: int):
        self.v: int = v
        self.w: int = w


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    b = Box(x, x)
    return b.v - b.w


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    assert f(P()) == 7
