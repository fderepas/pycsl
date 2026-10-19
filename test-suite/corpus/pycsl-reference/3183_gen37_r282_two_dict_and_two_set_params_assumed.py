r"""Test 3183 — route #282 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION PARAM-DISJOINT).

`f(d1, d2)` (`assigns d1`) stores `d1[1] = 5` and claims `d2[1] == 0`; `g(s1, s2)` (`assigns s1`)
adds 1 to `s1` and claims `not (1 in s2)`. Both PROVE: each dict/set parameter is its own region.
CPython violates both for `f(d, d)` / `g(s, s)`. A VERIFIED caller passing one dict/set to a mutating
slot and another slot of the same call is refused (route #254, PYCSL-WHYML-COLLECTION-ALIAS, corpus
3193). `--soundness-report` lists PARAM-DISJOINT for `f` and `g`. No strict mode.
"""
# pycsl-model-assumption: PARAM-DISJOINT
# pycsl-expected: PASS
from typing import Dict, Set


#@ requires 1 in d2 and d2[1] == 0
#@ ensures d2[1] == 0
#@ assigns d1
def f(d1: Dict[int, int], d2: Dict[int, int]) -> None:
    d1[1] = 5


#@ requires not (1 in s2)
#@ ensures not (1 in s2)
#@ assigns s1
def g(s1: Set[int], s2: Set[int]) -> None:
    s1.add(1)


if __name__ == "__main__":
    d = {1: 0}
    f(d, d)
    s: Set[int] = set()
    g(s, s)
    print(d, s)  # {1: 5} {1}: both claims are FALSE for the aliased calls
    assert d[1] == 5 and 1 in s
