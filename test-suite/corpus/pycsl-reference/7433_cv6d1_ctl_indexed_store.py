r"""Test 7433 -- cv6 D1 (expected PASS): CONTROL -- the refusal's advised rewrite of 7430/7431, an explicit indexed store `d[k] = []` instead of `d.setdefault(k, [])`, verifies the membership it creates.
"""
# pycsl-expected: PASS
from typing import Dict, List


#@ requires not (k in d)
#@ ensures \result == 1
#@ assigns d
def f(d: Dict[int, List[int]], k: int) -> int:
    d[k] = []
    return 1 if k in d else 0
