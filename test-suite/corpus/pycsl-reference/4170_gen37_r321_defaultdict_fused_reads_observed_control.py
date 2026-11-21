r"""Test 4170 -- gen #37 route #321 (expected PASS): CONTROL: `d[3] = d[3] + 7; d[4] += 1; 3 in d and 4 in d` -- every read fused into a store of the same key, so membership is faithful: PROVES.
"""
# pycsl-expected: PASS
from typing import Dict
from collections import defaultdict
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = defaultdict(int)
    d[3] = d[3] + 7
    d[4] += 1
    if 3 in d and 4 in d:
        return 7
    return 0

if __name__ == "__main__":
    assert f() == 7, f()
