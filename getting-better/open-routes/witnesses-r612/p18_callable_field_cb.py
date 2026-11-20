from typing import Callable
class Holder:
    def __init__(self, cb: Callable[[int], int]) -> None:
        self.cb: Callable[[int], int] = cb
#@ ensures \result == True
#@ assigns \nothing
def same(h: Holder, x: int) -> bool:
    return h.cb(x) == h.cb(x)
if __name__ == "__main__":
    import itertools
    it = itertools.count()
    r = same(Holder(lambda s: next(it)), 0)
    print("VIOLATION" if r is not True else "ok", r)
