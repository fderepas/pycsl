r"""Test 3340 -- route #287 (expected FAIL): `sorted(xs, key=lambda v: 10 // v)` under `no_exception \all` PROVED (the key body was dropped: `sorted_perm_1 xs`); CPython raises ZeroDivisionError on `[0, 1]`.
Now refused (a lambda's body contains a division).
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(xs: List[int]) -> List[int]:
    return sorted(xs, key=lambda v: 10 // v)


if __name__ == "__main__":
    try:
        f([0, 1])
        raise AssertionError("expected ZeroDivisionError")
    except ZeroDivisionError:
        pass
