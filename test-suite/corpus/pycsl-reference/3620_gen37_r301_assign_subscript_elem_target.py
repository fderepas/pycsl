r"""Test 3620 -- gen #37 route #301 (expected FAIL): REFUSAL: a SUBSCRIPT element in an assignment tuple target `a[0], t = p` (L3-tc at base) is refused at emit (PYCSL-UNPACK-TARGET). CPython g((5, 6)) == 5.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ ensures \result == 0
#@ assigns \nothing
def g(p: Tuple[int, int]) -> int:
    a = [0, 0]
    a[0], t = p
    return a[0]

if __name__ == "__main__":
    assert g((5, 6)) == 5
