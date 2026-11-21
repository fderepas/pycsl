r"""Test 9632 -- route #592 WITNESS (expected FAIL: the claim is FALSE of the program): `g` compares the truthiness of `d` with `len(d) != 0`; for every map they agree, so `\result == 1` holds of the verified body, and `h`'s call `g(3)` omits `d` (the opaque map `pycsl_none_map` since lvN), so `h`'s `\result == 1` followed. CPython passes `None`: `len(None)` raises TypeError, `h()` never returns 1. Refused PYCSL-R592-NONE-DEFAULT-MAP-CONCRETE.
"""
# pycsl-expected: FAIL
from typing import Dict, Optional


#@ ensures \result == 1
#@ assigns \nothing
def g(x: int, d: Optional[Dict[str, int]] = None) -> int:
    return 1 if bool(d) == (len(d) != 0) else 0


#@ ensures \result == 1
#@ assigns \nothing
def h() -> int:
    return g(3)


if __name__ == "__main__":
    print("result", h())   # CPython: TypeError (len of None)
