from typing import Callable
#@ ensures \result == True
#@ assigns \nothing
def same(f: Callable[[int], int], x: int) -> bool:
    h = lambda y: f(y)
    return h(x) == h(x)
if __name__ == "__main__":
    import itertools
    it = itertools.count()
    r = same(lambda s: next(it), 0)
    print("VIOLATION" if r is not True else "ok", r)
