r"""Test 9640 -- route #592 CONTROL (expected PASS): the callee of an omitted `Optional[Dict[str, str]] = None` argument is `#@ \trusted`, so no verified body reads the opaque `pycsl_none_map` and R592 does not fire; the caller's claim follows from the callee's contract (`g(3) == 3`, so `h() == 4`), which CPython satisfies (`g` returns `x`; result 4).
"""
# pycsl-expected: PASS
from typing import Dict, Optional


#@ \trusted reviewer: test-9640
#@ ensures \result == x
#@ assigns \nothing
def g(x: int, d: Optional[Dict[str, str]] = None) -> int:
    return x


#@ ensures \result == 4
#@ assigns \nothing
def h() -> int:
    y = g(3)
    return y + 1


if __name__ == "__main__":
    print("result", h())   # CPython: result 4
