r"""Test 9634 -- route #592 WITNESS (expected FAIL: the claim is FALSE of the program): `h` calls `g(3, y=1)`, binding `y` by keyword and OMITTING the middle parameter `d: Optional[Dict[str, List[int]]] = None` (filled with the opaque map `pycsl_none_map` since lvN). `g`'s verified body proves `\result == y + 1` because `isinstance(d, dict)` is true of every map, so `h`'s `\result == 2` followed. CPython passes `None`: `g(3, y=1)` returns 1. Refused PYCSL-R592-NONE-DEFAULT-MAP-CONCRETE.
"""
# pycsl-expected: FAIL
from typing import Dict, List, Optional


#@ ensures \result == y + 1
#@ assigns \nothing
def g(x: int, d: Optional[Dict[str, List[int]]] = None, y: int = 0) -> int:
    return y + 1 if isinstance(d, dict) else y


#@ ensures \result == 2
#@ assigns \nothing
def h() -> int:
    return g(3, y=1)


if __name__ == "__main__":
    print("result", h())   # CPython: result 1
