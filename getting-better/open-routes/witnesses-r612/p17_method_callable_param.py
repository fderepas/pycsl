from typing import Callable
class K:
    def __init__(self) -> None:
        self.v: int = 0
    #@ ensures \result == True
    #@ assigns \nothing
    def same(self, f: Callable[[int], int], x: int) -> bool:
        return f(x) == f(x)
if __name__ == "__main__":
    import itertools
    it = itertools.count()
    r = K().same(lambda s: next(it), 0)
    print("VIOLATION" if r is not True else "ok", r)
