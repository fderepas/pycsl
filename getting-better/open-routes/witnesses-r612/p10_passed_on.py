from typing import Callable
#@ ensures \result == f(x)
#@ assigns \nothing
def app(f: Callable[[int], int], x: int) -> int:
    return f(x)
#@ ensures \result == True
#@ assigns \nothing
def same(f: Callable[[int], int], x: int) -> bool:
    return app(f, x) == app(f, x)
if __name__ == "__main__":
    import itertools
    it = itertools.count()
    r = same(lambda s: next(it), 0)
    print("VIOLATION" if r is not True else "ok", r)
