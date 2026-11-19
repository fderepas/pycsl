r"""Test 9592 -- route #589 WITNESS (expected FAIL: REFUSED PYCSL-R589-RAISE-ARGUMENT-UNEVALUATED at HEAD, every model; PROVED at base, rt56 ha1760): an f-string second argument `f"{xs[9]}"` is dropped with its IndexError. CPython: IndexError.
"""
# pycsl-expected: FAIL
from typing import List


class E(Exception):
    pass


#@ no_exception \all
#@ ensures \result == 1
def f(xs: List[int]) -> int:
    try:
        raise E("a", f"{xs[9]}")
    except E:
        return 1
    return 0


if __name__ == "__main__":
    try:
        print(f([1]))
    except Exception as e:
        print("VIOLATION", type(e).__name__)
