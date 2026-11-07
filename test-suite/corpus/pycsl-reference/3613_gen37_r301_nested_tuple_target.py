r"""Test 3613 -- gen #37 route #301 (expected FAIL): REFUSAL: a NESTED tuple target `(u, (v1, v2)) = p` kept only `u`, so `v1` stayed 0 and `\result == 0` PROVED; CPython g((1, (2, 3))) == 2. Refused at emit (PYCSL-UNPACK-TARGET).
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ ensures \result == 0
#@ assigns \nothing
def g(p: Tuple[int, Tuple[int, int]]) -> int:
    v1 = 0
    (u, (v1, v2)) = p
    return v1

if __name__ == "__main__":
    assert g((1, (2, 3))) == 2
