r"""Test 5066 -- gen #37 route #375 (expected FAIL): `[*self]` on a field-less class under `no_exception \all` lowered as the one-element array `[self]`, PROVED (CPython TypeError: not iterable). FAILS now (PyCSL-R375 assertion).
"""
# pycsl-expected: FAIL
from typing import List

class W:
    pass

    #@ no_exception \all
    def m(self) -> int:
        xs = [*self]
        return 0

if __name__ == "__main__":
    print(W().m())
