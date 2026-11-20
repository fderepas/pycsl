from typing import Callable
#@ ensures \result == True
#@ assigns \nothing
def same(f: Callable[[str], int], s: str) -> bool:
    return f(s) == f(s)
if __name__ == "__main__":
    import itertools
    it = itertools.count()
    r = same(lambda s: next(it), "a")
    print("VIOLATION" if r is not True else "ok", r)
