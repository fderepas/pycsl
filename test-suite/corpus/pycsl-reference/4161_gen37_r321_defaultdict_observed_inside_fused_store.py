r"""Test 4161 -- gen #37 route #321 (expected FAIL): `d[5] = d[5] + len(d)`: the read inserts BEFORE `len(d)` is evaluated (CPython 1). A fused store whose value mentions `d` again is not fused: REFUSED.
"""
# pycsl-expected: FAIL
from typing import Dict
from collections import defaultdict
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = defaultdict(int)
    d[5] = d[5] + len(d)
    return d[5]

if __name__ == "__main__":
    assert f() == 0, f()
