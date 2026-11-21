r"""Test 4912 -- gen #37 route #365 (expected FAIL): `{(xs, 1)}` with `xs: List[int]` (CPython TypeError: unhashable list inside the tuple). REFUSED now (route #365).
"""
# pycsl-expected: FAIL
from typing import List

#@ no_exception \all
#@ ensures \result == 1
def g(xs: List[int]) -> int:
    s = {(xs, 1)}
    return 1

if __name__ == "__main__":
    print(g([1]))
