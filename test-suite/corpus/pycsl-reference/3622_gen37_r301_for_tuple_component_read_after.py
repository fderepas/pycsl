r"""Test 3622 -- gen #37 route #301 (expected FAIL): REFUSAL: a FLAT tuple for-target component read AFTER the loop (`u = 0; for u, v in ps: pass; return u`) kept its PRE-loop value (no write-back), so `\result == 0` PROVED; CPython g([(7, 8)]) == 7. Refused at emit (route #301).
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(ps) == 1
#@ ensures \result == 0
#@ assigns \nothing
def g(ps: List[Tuple[int, int]]) -> int:
    u = 0
    for u, v in ps:
        pass
    return u

if __name__ == "__main__":
    assert g([(7, 8)]) == 7
