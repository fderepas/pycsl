r"""Test 4913 -- gen #37 route #366 (expected FAIL): frozen dataclass with an `object` field holding a list; `{d}` PROVED (CPython TypeError). REFUSED now (route #366).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass(frozen=True)
class D:
    xs: object

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D([1, 2])))
