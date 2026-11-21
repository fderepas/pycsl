from typing import Callable
class Box:
    def __init__(self, f: Callable[[int], int]) -> None:
        self.f: Callable[[int], int] = f
#@ ensures \result == True
#@ assigns \nothing
def same(b: Box, x: int) -> bool:
    return b.f(x) == b.f(x)
if __name__ == "__main__":
    import itertools
    it = itertools.count()
    r = same(Box(lambda s: next(it)), 0)
    print("VIOLATION" if r is not True else "ok", r)
