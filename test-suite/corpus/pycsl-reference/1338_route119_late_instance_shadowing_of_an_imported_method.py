r"""Test 1338 — ROUTE #119 (late instance shadowing): `class C(K)` with `K` imported; `install()` stores `self.m = int` OUTSIDE `__init__` (so no record field exists) and `c.m()` PROVED `K.m`s contract `\result == 1` while CPython returns 0. Refused where the IR knows the call resolves to a method AND an attribute of that name is stored.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r119_plainlib import K


class C(K):
    def __init__(self) -> None:
        self.a = 0

    #@ assigns self.m
    def install(self) -> None:
        self.m = int


#@ assigns c.m
#@ ensures \result == 1
def f() -> int:
    c = C()
    c.install()
    return c.m()
