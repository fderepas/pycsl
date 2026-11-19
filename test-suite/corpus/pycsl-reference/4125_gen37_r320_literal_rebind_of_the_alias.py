r"""Test 4125 -- gen #37 route #320 (expected FAIL): `ys = xs; ys = [7, 8]; return xs[0]` rebinding the ALIAS overwrote the shared array; `\result == 7` would prove (CPython 1). REFUSED.
"""
# pycsl-expected: FAIL
from typing import List

#@ ensures \result == 7
def f() -> int:
    xs = [1, 2]
    ys = xs
    ys = [7, 8]
    return xs[0]

if __name__ == "__main__":
    assert f() == 7, f()
