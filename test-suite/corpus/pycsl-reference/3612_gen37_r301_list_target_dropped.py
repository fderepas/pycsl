r"""Test 3612 -- gen #37 route #301 (expected FAIL): REFUSAL: a plain LIST target `[u, t] = e` had no emitter arm and emitted NOTHING, so `\result == 0` PROVED; CPython g([3, 4]) == 4. Refused at emit (PYCSL-UNPACK-TARGET).
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(e) == 2
#@ ensures \result == 0
#@ assigns \nothing
def g(e: List[int]) -> int:
    t = 0
    u = 0
    [u, t] = e
    return t

if __name__ == "__main__":
    assert g([3, 4]) == 4
