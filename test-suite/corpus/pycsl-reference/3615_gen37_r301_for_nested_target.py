r"""Test 3615 -- gen #37 route #301 (expected FAIL): REFUSAL: a NESTED for-target `for a, (b, c) in ps` bound `(b, c)` to a `_` placeholder, so `b` stayed 0 and `\result == 0` PROVED; CPython g([(1, (2, 3))]) == 2. Refused at emit (PYCSL-UNPACK-TARGET).
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(ps) == 1
#@ ensures \result == 0
#@ assigns \nothing
def g(ps: List[Tuple[int, Tuple[int, int]]]) -> int:
    b = 0
    for a, (b, c) in ps:
        pass
    return b

if __name__ == "__main__":
    assert g([(1, (2, 3))]) == 2
