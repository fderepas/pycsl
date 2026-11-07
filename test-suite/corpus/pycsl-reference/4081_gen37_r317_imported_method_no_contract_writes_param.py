r"""Test 4081 -- gen #37 route #317 (expected FAIL): imported class method `h.poke(ys)` writes its argument; `ys[0] == 0` PROVED (CPython 5). FAILS.
"""
# pycsl-expected: FAIL
from typing import List
from multi_file_lib.rt16helper import H

#@ ensures \result == 0
def f() -> int:
    ys = [0]
    h = H()
    h.poke(ys)
    return ys[0]

if __name__ == "__main__":
    assert f() == 0, f()
