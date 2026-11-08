r"""Test 3908 -- gen #37 route #307 (expected FAIL): dict literal `{inc(xs): inc(xs)}` evaluated value before key (now REFUSED); Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe r01_dict_lit).
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == False
def f() -> bool:
    xs = [0]
    d: Dict[int, int] = {inc(xs): inc(xs)}
    return 1 in d

if __name__ == "__main__":
    assert f() == False
