r"""Test 10175 -- route #612 (expected FAIL): an annotated local alias `g: Callable[[int], int] = f` of a `Callable` parameter, then `g(x) == g(x)`. The alias is itself `Callable`-typed and was lowered to the same pure function, so `ensures \result == True` was decided True at base 0057c8b94; CPython with `itertools.count` returns False (the driver prints VIOLATION). Now REFUSED (PYCSL-R612-CALLABLE-ASSUMED-PURE).
"""
# pycsl-expected: FAIL
from typing import Callable


#@ ensures \result == True
#@ assigns \nothing
def same(f: Callable[[int], int], x: int) -> bool:
    g: Callable[[int], int] = f
    return g(x) == g(x)


if __name__ == "__main__":
    import itertools
    it = itertools.count()
    r = same(lambda s: next(it), 0)
    print("VIOLATION" if r is not True else "result", r)
