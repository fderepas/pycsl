r"""Test 4761 -- gen #37 route #355 (expected FAIL): `C(99)` on a dunder-free IntEnum under `no_exception \all` PROVED (emitted `any c`; CPython ValueError). REFUSED now (route #355).
"""
# pycsl-expected: FAIL
from enum import IntEnum

class C(IntEnum):
    A = 1

#@ no_exception \all
def f() -> int:
    x = C(99)
    return 0

if __name__ == "__main__":
    f()
