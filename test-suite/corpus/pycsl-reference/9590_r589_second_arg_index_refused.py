r"""Test 9590 -- route #589 WITNESS (expected FAIL: REFUSED PYCSL-R589-RAISE-ARGUMENT-UNEVALUATED at HEAD, every model; PROVED at base, red team rt56 ha1758): `raise E("a", xs[9])` dropped its second constructor argument, so the IndexError CPython raises before building E was absent and `except E` proved `no_exception \all` + `\result == 1`. CPython: IndexError.
"""
# pycsl-expected: FAIL
from typing import List


class E(Exception):
    pass


#@ no_exception \all
#@ ensures \result == 1
def f(xs: List[int], k: int) -> int:
    try:
        raise E("a", xs[9])
    except E:
        return 1
    return 0


if __name__ == "__main__":
    try:
        print(f([1], 0))
    except Exception as e:
        print("VIOLATION", type(e).__name__)
