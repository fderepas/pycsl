from typing import Callable, List
#@ ensures \result == True
#@ assigns \nothing
def same(f: Callable[[int], int], xs: List[int]) -> bool:
    return list(map(f, xs)) == list(map(f, xs))
if __name__ == "__main__":
    import itertools
    it = itertools.count()
    r = same(lambda s: next(it), [1])
    print("VIOLATION" if r is not True else "ok", r)
