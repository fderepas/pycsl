r"""Test 3193 — route #282 VERIFIED-CALLER ALIAS CONTROL (expected FAIL): the dict callee of 3183 called from VERIFIED code as `f(d, d)`.
`g` claims `\result == 0`; CPython returns 5. REFUSED (route #254, PYCSL-WHYML-COLLECTION-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict
#@ requires 1 in d2 and d2[1] == 0
#@ ensures d2[1] == 0
#@ assigns d1
def f(d1: Dict[int, int], d2: Dict[int, int]) -> None:
    d1[1] = 5

#@ ensures \result == 0
def g() -> int:
    d = {1: 0}
    f(d, d)
    return d[1]


if __name__ == "__main__":
    print(g())  # 5
    assert g() == 5
