r"""Test 10174 -- route #612 (expected FAIL): `f.__call__(x) == f.__call__(x)` on a `Callable` parameter lowered to an abstract pure `val f___call___1`, so `ensures \result == True` PROVED at base 0057c8b94; CPython with `itertools.count` returns False (the driver prints VIOLATION). Now REFUSED (PYCSL-R612-CALLABLE-ASSUMED-PURE).
"""
# pycsl-expected: FAIL
from typing import Callable


#@ ensures \result == True
#@ assigns \nothing
def same(f: Callable[[int], int], x: int) -> bool:
    return f.__call__(x) == f.__call__(x)


if __name__ == "__main__":
    import itertools
    it = itertools.count()
    r = same(lambda s: next(it), 0)
    print("VIOLATION" if r is not True else "result", r)
