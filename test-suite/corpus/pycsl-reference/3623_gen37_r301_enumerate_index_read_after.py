r"""Test 3623 -- gen #37 route #301 (expected FAIL): REFUSAL: an `enumerate` tuple for-target index read AFTER the loop (`i = 0; for i, x in enumerate(e): pass; return i`) kept 0, so `\result == 0` PROVED; CPython g(["a", "b"]) == 1. Refused at emit (route #301).
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(e) == 2
#@ ensures \result == 0
#@ assigns \nothing
def g(e: List[str]) -> int:
    i = 0
    for i, x in enumerate(e):
        pass
    return i

if __name__ == "__main__":
    assert g(["a", "b"]) == 1
