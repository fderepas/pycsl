r"""Test 9630 -- route #592 WITNESS (expected FAIL: the claim is FALSE of the program): `h` calls `g(3)`, omitting `d: Optional[Dict[str, str]] = None`. Since lvN the omitted default is the opaque map `pycsl_none_map`, and `g`'s VERIFIED body reads `d` as a map, where `isinstance(d, dict)` is always true, so `g`'s `\result == 1` held for every map and `h`'s `\result == 1` PROVED. CPython passes `None`: `g(3)` returns 0. Refused PYCSL-R592-NONE-DEFAULT-MAP-CONCRETE.
"""
# pycsl-expected: FAIL
from typing import Dict, Optional


#@ ensures \result == 1
#@ assigns \nothing
def g(x: int, d: Optional[Dict[str, str]] = None) -> int:
    return 1 if isinstance(d, dict) else 0


#@ ensures \result == 1
#@ assigns \nothing
def h() -> int:
    return g(3)


if __name__ == "__main__":
    print("result", h())   # CPython: result 0
