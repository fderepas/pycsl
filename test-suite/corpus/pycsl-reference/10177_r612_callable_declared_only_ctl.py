r"""Test 10177 -- route #612 CONTROL (expected PASS): a `Callable` parameter that is DECLARED and never referenced is not refused, and the function's claim about its other arguments still proves. The route #612 rule refuses only an application or another reference of the `Callable` name.
"""
# pycsl-expected: PASS
from typing import Callable


#@ ensures \result == x + 1
#@ assigns \nothing
def g(f: Callable[[int], int], x: int) -> int:
    return x + 1


if __name__ == "__main__":
    import itertools
    it = itertools.count()
    print("result", g(lambda y: next(it), 1))
