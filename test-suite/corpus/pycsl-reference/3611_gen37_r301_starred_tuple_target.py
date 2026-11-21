r"""Test 3611 -- gen #37 route #301 (expected FAIL): REFUSAL: a starred TUPLE target `*h, t = e` lost its starred element (L3-tc at base); refused at emit (PYCSL-UNPACK-TARGET). CPython g([3, 4]) == 4.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(e) == 2
#@ ensures \result == 0
#@ assigns \nothing
def g(e: List[int]) -> int:
    t = 0
    *h, t = e
    return t

if __name__ == "__main__":
    assert g([3, 4]) == 4
