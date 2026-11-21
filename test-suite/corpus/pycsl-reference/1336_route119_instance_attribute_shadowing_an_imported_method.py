r"""Test 1336 — ROUTE #119 (instance level, imported base): `class C(K)` with `K` imported, `self.m = int` shadows the INHERITED method `m`; `C().m()` PROVED `K.m`s contract `\result == 1` while CPython returns 0. A front-end check cannot see the imported base, so the refusal lives where the IR knows both the field and the method (PYCSL-WHYML-METHOD-SHADOWED).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r119_plainlib import K


class C(K):
    def __init__(self) -> None:
        self.a = 0
        self.m = int


#@ ensures \result == 1
def f() -> int:
    c = C()
    return c.m()
