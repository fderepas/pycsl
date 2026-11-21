r"""Test 3342 -- route #287 (expected FAIL): `sorted(xs, key=lambda v: xs[v])` under `no_exception \all` PROVED; CPython raises IndexError for `[3]`.
Now refused.
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(xs: List[int]) -> List[int]:
    return sorted(xs, key=lambda v: xs[v])


if __name__ == "__main__":
    try:
        f([3])
        raise AssertionError("expected IndexError")
    except IndexError:
        pass
