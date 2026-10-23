r"""Test 4171 -- gen #37 route #321 (expected PASS): CONTROL: two `Counter([1, 1])` from EQUAL literal seeds denote equal maps: PROVES.
"""
# pycsl-expected: PASS
from typing import Dict
from collections import Counter
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c1: Dict[int, int] = Counter([1, 1])
    c2: Dict[int, int] = Counter([1, 1])
    if c1[1] != c2[1]:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 0, f()
