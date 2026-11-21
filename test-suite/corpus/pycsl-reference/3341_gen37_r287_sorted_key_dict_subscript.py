r"""Test 3341 -- route #287 (expected FAIL): `sorted(xs, key=lambda v: d[v])` under `no_exception \all` PROVED; CPython raises KeyError for `([3], {})`.
Now refused (a lambda's body contains a subscript).
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ no_exception \all
def f(xs: List[int], d: Dict[int, int]) -> List[int]:
    return sorted(xs, key=lambda v: d[v])


if __name__ == "__main__":
    try:
        f([3], {})
        raise AssertionError("expected KeyError")
    except KeyError:
        pass
