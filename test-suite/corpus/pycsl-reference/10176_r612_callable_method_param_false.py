r"""Test 10176 -- route #612 (expected FAIL): the same pure lowering for a `Callable` parameter of a METHOD: `f(x) == f(x)` with `ensures \result == True` PROVED at base 0057c8b94 (hoare, typed and store); CPython with `itertools.count` returns False (the driver prints VIOLATION). Now REFUSED (PYCSL-R612-CALLABLE-ASSUMED-PURE).
"""
# pycsl-expected: FAIL
from typing import Callable


class K:
    #@ assigns \nothing
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
    print("VIOLATION" if r is not True else "result", r)
