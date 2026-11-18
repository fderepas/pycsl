from typing import Callable, List
#@ ensures \result == True
#@ assigns \nothing
def same(f: Callable[[int], int], xs: List[int]) -> bool:
    return sorted(xs, key=f) == sorted(xs, key=f)
if __name__ == "__main__":
    import itertools
    it = itertools.count()
    r = same(lambda s: next(it) % 3, [1, 2])
    print("VIOLATION" if r is not True else "ok", r)
