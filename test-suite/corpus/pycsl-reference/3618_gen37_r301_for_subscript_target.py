r"""Test 3618 -- gen #37 route #301 (expected FAIL): REFUSAL: a SUBSCRIPT for-target `for a[0] in [7]` (became `_for_target`; L3-tc at base) is refused at emit (PYCSL-UNPACK-TARGET). CPython g([(1, 2)]) == 7.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(ps) == 1
#@ ensures \result == 0
#@ assigns \nothing
def g(ps: List[Tuple[int, int]]) -> int:
    a = [0, 0]
    for a[0] in [7]:
        pass
    return a[0]

if __name__ == "__main__":
    assert g([(1, 2)]) == 7
