from typing import Callable
#@ ensures \result == True
#@ assigns \nothing
def same(f: Callable[[int], int], x: int) -> bool:
    return f.__call__(x) == f.__call__(x)
if __name__ == "__main__":
    import itertools
    it = itertools.count()
    r = same(lambda s: next(it), 0)
    print("VIOLATION" if r is not True else "ok", r)
