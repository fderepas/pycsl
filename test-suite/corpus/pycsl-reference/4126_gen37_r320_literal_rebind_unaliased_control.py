r"""Test 4126 -- gen #37 route #320 (expected PASS): CONTROL: an unaliased list local rebound to a literal (`t = xs[0]; xs = [7, 8]`) keeps the in-place lowering; `\result == 8` proves.
"""
# pycsl-expected: PASS
from typing import List

#@ ensures \result == 8
def f() -> int:
    xs = [1, 2]
    t = xs[0]
    xs = [7, 8]
    return xs[0] + t

if __name__ == "__main__":
    assert f() == 8, f()
