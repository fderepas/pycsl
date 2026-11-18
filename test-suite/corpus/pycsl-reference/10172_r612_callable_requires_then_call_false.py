r"""Test 10172 -- route #612 (expected FAIL): `requires f(x) >= 0` then `return f(x)` with `ensures \result >= 0` PROVED at base 0057c8b94 (hoare; typed / store fail there on the pre-existing "depends on external variables" `let function` error) (the old shape of control 1878): the precondition's application was assumed to be the body's call. CPython: the caller checks `h(0) >= 0` (1), the body's call returns -1 (the driver prints VIOLATION). Now REFUSED (PYCSL-R612-CALLABLE-ASSUMED-PURE).
"""
# pycsl-expected: FAIL
from typing import Callable


#@ requires f(x) >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def app(f: Callable[[int], int], x: int) -> int:
    return f(x)


if __name__ == "__main__":
    import itertools
    c = itertools.count()
    h = lambda y: 1 if next(c) == 0 else -1
    assert h(0) >= 0
    r = app(h, 0)
    print("VIOLATION" if r < 0 else "result", r)
