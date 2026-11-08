r"""Test 8029 -- route #506 (control, expected PASS): the honest shape of 6783 (now refused: a method call drops a subscript receiver) with the advice followed -- the list element is bound by a plain statement first, under a guard that discharges its IndexError obligation (`#@ no_exception \all`), then used as the method receiver; CPython f(["ab"]) returns 2
"""
# pycsl-expected: PASS
from typing import List


#@ no_exception \all
#@ ensures \result == 0 or \result == len(xs[0])
def f(xs: List[str]) -> int:
    if len(xs) == 0:
        return 0
    x = xs[0]
    k = len(x.upper())
    return len(x)


if __name__ == "__main__":
    print("result", f(["ab"]))
