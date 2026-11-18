r"""Test 10134 -- run #8 batch B, u48 rule R4 (expected FAIL): `x.rfind("a") == y.rfind("a")` claimed always equal (CPython 1 vs 0 for ("ba", "a")): `str.rfind` has no model and the generic `<recv>_rfind_<n>` fallback DROPS the receiver, so the result is input-blind (cv14 gap b). REFUSED: PYCSL-CV14-STR-RFIND-RECEIVER-DROPPED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple

#@ ensures \result == 1
#@ assigns \nothing
def f(x: str, y: str) -> int:
    if x.rfind("a") == y.rfind("a"):
        return 1
    return 0

if __name__ == "__main__":
    r = f("ba", "a")
    print("VIOLATION contract" if r != 1 else "result", r)
