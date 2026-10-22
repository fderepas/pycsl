r"""Test 3614 -- gen #37 route #301 (expected FAIL): REFUSAL: a LIST for-target `for [t] in e` became `_for_target`, so `t` stayed 0 and `\result == 0` PROVED; CPython g([[7]]) == 7. Refused at emit (PYCSL-UNPACK-TARGET).
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(e) >= 1
#@ ensures \result == 0
#@ assigns \nothing
def g(e: List[List[int]]) -> int:
    t = 0
    for [t] in e:
        pass
    return t

if __name__ == "__main__":
    assert g([[7]]) == 7
