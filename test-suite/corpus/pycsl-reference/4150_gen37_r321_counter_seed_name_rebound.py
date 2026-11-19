r"""Test 4150 -- gen #37 route #321 (expected FAIL): `Counter(xs)` before and after `xs = [2]` shared ONE constant keyed on the text `xs`; `c1[1] != c2[1]` was decided False (CPython True). A non-literal seed is now REFUSED.
"""
# pycsl-expected: FAIL
from collections import Counter
from typing import Dict
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    xs = [1, 1]
    c1: Dict[int, int] = Counter(xs)
    xs = [2]
    c2: Dict[int, int] = Counter(xs)
    if c1[1] != c2[1]:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 0, f()
