r"""Test 4918 -- gen #37 route #366 (expected FAIL): NamedTuple with an `object` field holding a list; `{n}` PROVED (CPython TypeError). REFUSED now (route #366).
"""
# pycsl-expected: FAIL
from typing import NamedTuple

class N(NamedTuple):
    xs: object

#@ no_exception \all
#@ ensures \result == 1
def g(n: N) -> int:
    s = {n}
    return 1

if __name__ == "__main__":
    print(g(N([1])))
