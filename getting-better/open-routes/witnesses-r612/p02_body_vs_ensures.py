from typing import Callable
#@ ensures \result == f(x)
#@ assigns \nothing
def app(f: Callable[[int], int], x: int) -> int:
    return f(x)
if __name__ == "__main__":
    import itertools
    it = itertools.count()
    g = lambda x: next(it)
    r = app(g, 0)
    print("VIOLATION" if r != g(0) else "ok", r)
