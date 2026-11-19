r"""Test 4620 -- gen #37 route #343 (expected FAIL): witness l06: `xs: List[int] = [self]; xs[0] + 1` under `no_exception \all`; PROVED (CPython TypeError). REFUSED / FAIL (erased element).
"""
# pycsl-expected: FAIL
from typing import List
class P:
    #@ no_exception \all
    def m(self) -> int:
        xs: List[int] = [self]
        return xs[0] + 1

if __name__ == "__main__":
    try:
        P().m()
        assert False, "expected TypeError"
    except TypeError:
        pass
