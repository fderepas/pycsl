r"""Test 3616 -- gen #37 route #301 (expected FAIL): REFUSAL: a STARRED for-target `for *b, a in ps` dropped the binding of `a`, so `\result == 0` PROVED; CPython g([(1, 2)]) == 2. Refused at emit (PYCSL-UNPACK-TARGET).
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(ps) == 1
#@ ensures \result == 0
#@ assigns \nothing
def g(ps: List[Tuple[int, int]]) -> int:
    a = 0
    for *b, a in ps:
        pass
    return a

if __name__ == "__main__":
    assert g([(1, 2)]) == 2
