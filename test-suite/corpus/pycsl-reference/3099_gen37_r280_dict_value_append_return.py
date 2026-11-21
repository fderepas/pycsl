r"""Test 3099 — route #280 (expected FAIL): `d[0].append(1); return len(d[0])` with
`\result == \old(len(d[0]))` PROVED at 72ab1c57 (red-team p240). CPython: one more. Now refused.
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ requires 0 in d
#@ ensures \result == \old(len(d[0]))
#@ assigns d
def f(d: Dict[int, List[int]]) -> int:
    d[0].append(1)
    return len(d[0])


if __name__ == "__main__":
    assert f({0: []}) == 1
