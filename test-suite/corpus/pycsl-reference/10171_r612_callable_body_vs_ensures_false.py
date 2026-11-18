r"""Test 10171 -- route #612 (expected FAIL): `ensures \result == f(x)` over a body `return f(x)` PROVED at base 0057c8b94 (hoare; typed / store fail there on the pre-existing "depends on external variables" `let function` error) (the contract's application and the body's call are the same pure WhyML term). In CPython the two are two calls: with a stateful callable the result differs from a later `f(x)` (the driver prints VIOLATION). This is also the shape of `typing-engagement/ty3/conformance_callable/S5_pass.py`. Now REFUSED (PYCSL-R612-CALLABLE-ASSUMED-PURE).
"""
# pycsl-expected: FAIL
from typing import Callable


#@ ensures \result == f(x)
#@ assigns \nothing
def app(f: Callable[[int], int], x: int) -> int:
    return f(x)


if __name__ == "__main__":
    import itertools
    it = itertools.count()
    g = lambda y: next(it)
    r = app(g, 0)
    print("VIOLATION" if r != g(0) else "result", r)
