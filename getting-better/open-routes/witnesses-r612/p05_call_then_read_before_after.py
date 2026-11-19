from typing import Callable
#@ ensures \result == 0
#@ assigns \nothing
def g(f: Callable[[int], int], x: int) -> int:
    a = f(x)
    y = x + 1
    b = f(x)
    return a - b
if __name__ == "__main__":
    import itertools
    it = itertools.count()
    r = g(lambda x: next(it), 0)
    print("VIOLATION" if r != 0 else "ok", r)
