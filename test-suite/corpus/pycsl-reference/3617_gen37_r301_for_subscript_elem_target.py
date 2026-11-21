r"""Test 3617 -- gen #37 route #301 (expected FAIL): REFUSAL: a SUBSCRIPT element in a for-target `for a[0], b in ps` was a `_` placeholder, so the store to `a[0]` vanished and `\result == 0` PROVED; CPython g([(5, 6)]) == 5. Refused at emit (PYCSL-UNPACK-TARGET).
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(ps) == 1
#@ ensures \result == 0
#@ assigns \nothing
def g(ps: List[Tuple[int, int]]) -> int:
    a = [0, 0]
    for a[0], b in ps:
        pass
    return a[0]

if __name__ == "__main__":
    assert g([(5, 6)]) == 5
