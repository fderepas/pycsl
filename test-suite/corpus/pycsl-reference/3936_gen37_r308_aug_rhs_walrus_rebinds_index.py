r"""Test 3936 -- gen #37 route #308 (expected FAIL): `ys[i] += (i := 2) + 3`: Python stores into ys[0] (index read first); the desugar re-read `i` after the walrus. Now REFUSED.
"""
# pycsl-expected: FAIL
from typing import List

#@ ensures \result == 0
def f() -> int:
    ys = [0, 0, 0]
    i = 0
    ys[i] += (i := 2) + 3
    return ys[0]

if __name__ == "__main__":
    assert f() == 0
