r"""Test 3610 -- gen #37 route #301 (expected FAIL): REFUSAL: a starred LIST target `[*h, t] = e` was DROPPED, so `t` kept 0 and `\result == 0` PROVED; CPython g([5]) == 5. Refused at emit (PYCSL-UNPACK-TARGET).
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(e) == 1
#@ ensures \result == 0
#@ assigns \nothing
def g(e: List[int]) -> int:
    t = 0
    [*h, t] = e
    return t

if __name__ == "__main__":
    assert g([5]) == 5
