r"""Test 4172 -- gen #37 route #321 (expected PASS): CONTROL: a defaultdict used only through subscripts (no observation of its key set): the read reads 0, PROVES.
"""
# pycsl-expected: PASS
from typing import Dict
from collections import defaultdict
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = defaultdict(int)
    x = d[5]
    d[2] = 3
    return x

if __name__ == "__main__":
    assert f() == 0, f()
