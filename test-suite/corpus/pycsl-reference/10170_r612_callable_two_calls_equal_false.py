r"""Test 10170 -- route #612 (expected FAIL): a `Callable[[str], int]` parameter was lowered to a PURE WhyML function `string -> int`, so `f(s) == f(s)` was decided True and `ensures \result == True` PROVED at base 0057c8b94. CPython with a stateful callable (`itertools.count`) returns False (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R612-CALLABLE-ASSUMED-PURE).
"""
# pycsl-expected: FAIL
from typing import Callable


#@ ensures \result == True
#@ assigns \nothing
def same(f: Callable[[str], int], s: str) -> bool:
    return f(s) == f(s)


if __name__ == "__main__":
    import itertools
    it = itertools.count()
    r = same(lambda s: next(it), "a")
    print("VIOLATION" if r is not True else "result", r)
