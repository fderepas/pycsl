r"""Test 3619 -- gen #37 route #301 (expected FAIL): REFUSAL: a NESTED comprehension target `[b for a, (b, c) in ps]` (L3-tc at base) is refused at emit (PYCSL-UNPACK-TARGET). CPython g([(1, (2, 3))]) == 2.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(ps) == 1
#@ ensures \result == 0
#@ assigns \nothing
def g(ps: List[Tuple[int, Tuple[int, int]]]) -> int:
    r = [b for a, (b, c) in ps]
    return r[0]

if __name__ == "__main__":
    assert g([(1, (2, 3))]) == 2
