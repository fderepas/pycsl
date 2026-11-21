r"""Test 5067 -- gen #37 route #375 (expected FAIL): `t = self; t += 1` under `no_exception \all`: R337 only sees `self` spelled directly; PROVED at base (CPython TypeError). FAILS now (PyCSL-R375).
"""
# pycsl-expected: FAIL
from typing import List

class W:
    pass

    #@ no_exception \all
    def m(self) -> int:
        t = self
        t += 1
        return 0

if __name__ == "__main__":
    print(W().m())
