r"""Test 4124 -- gen #37 route #320 (expected FAIL): `ys = xs; if True: xs = [7, 8]; return ys[0]`; `\result == 7` PROVED (CPython 1). REFUSED.
"""
# pycsl-expected: FAIL
from typing import List
class C:
    def __init__(self) -> None:
        self.n = 0

#@ ensures \result == 7
def f() -> int:
    xs = [1, 2]
    ys = xs
    if True:
        xs = [7, 8]
    return ys[0]

if __name__ == "__main__":
    assert f() == 7, f()
