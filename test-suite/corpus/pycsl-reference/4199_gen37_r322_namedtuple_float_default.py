r"""Test 4199 -- gen #37 route #322 (expected FAIL): NamedTuple `r: int = 2.5`; `P().r == 2` PROVED (default `int(2.5)`; CPython 2.5).
"""
# pycsl-expected: FAIL
from typing import NamedTuple

class P(NamedTuple):
    r: int = 2.5

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    p = P()
    if p.r == 2:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
