r"""Test 1344 — ROUTE #123 (imported base): `class B(K): m = lambda self: 2` with `K` imported (K.m -> 1); the imported method stub was cloned over the override and `B().m()` PROVED `\result == 1` while CPython returns 2. A front-end check cannot see K's methods; the clone is skipped now.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r119_plainlib import K


class B(K):
    m = lambda self: 2

    def __init__(self) -> None:
        self.a = 0


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    b = B()
    return b.m()
