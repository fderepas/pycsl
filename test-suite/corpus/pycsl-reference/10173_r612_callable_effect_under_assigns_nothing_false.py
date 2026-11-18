r"""Test 10173 -- route #612 (expected FAIL): a call of a `Callable` parameter was assumed to change nothing. `requires len(xs) == 1` / `f(0)` / `return len(xs)` with `ensures \result == 1` PROVED at base 0057c8b94; CPython with a callable that appends to the caller's list returns 2 (the driver prints VIOLATION). Now REFUSED (PYCSL-R612-CALLABLE-ASSUMED-PURE).
"""
# pycsl-expected: FAIL
from typing import Callable, List


#@ requires len(xs) == 1
#@ ensures \result == 1
def g(f: Callable[[int], int], xs: List[int]) -> int:
    f(0)
    return len(xs)


if __name__ == "__main__":
    ys = [0]
    r = g(lambda y: ys.append(7) or 0, ys)
    print("VIOLATION" if r != 1 else "result", r)
