r"""Test 1339 — ROUTE #119 (non-literal setattr over an imported base): `class C(K)` with `K` imported and only `__init__(self, name, value): setattr(self, name, value)`; `C("m", int).m()` PROVED `K.m`s contract `\result == 1` while CPython returns 0. A non-literal setattr on self is refused in a class with an unseen (foreign) base.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r119_plainlib import K


class C(K):
    def __init__(self, name, value) -> None:
        self.a = 0
        setattr(self, name, value)


#@ ensures \result == 1
def f() -> int:
    c = C("m", int)
    return c.m()
