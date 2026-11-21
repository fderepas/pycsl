r"""Test 3925 -- gen #37 route #307 (expected FAIL): REFUSAL witness: `has1(mk(xs), inc(xs))` where the EFFECTFUL first argument returns a dict (a mutable container Why3 models as a value): binding it would snapshot the dict, leaving it inline would run `mk` after `inc`; refused.
"""
# pycsl-expected: FAIL
from typing import List, Tuple, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == a - b
def sub(a: int, b: int) -> int:
    return a - b
def mk(a: List[int]) -> Dict[int, int]:
    a[0] = a[0] + 1
    return {1: a[0]}

#@ assigns \nothing
def has1(d: Dict[int, int], z: int) -> bool:
    return 1 in d

#@ ensures \result == True
def f() -> bool:
    xs = [0]
    return has1(mk(xs), inc(xs))

if __name__ == "__main__":
    assert f() == True
