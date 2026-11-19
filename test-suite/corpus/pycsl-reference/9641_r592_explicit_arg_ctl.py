r"""Test 9641 -- route #592 CONTROL (expected PASS): the same verified callee as witness 9630, but the caller passes `d` EXPLICITLY (a real dict), so nothing is filled and R592 does not fire; `isinstance(d, dict)` is true for the dict CPython passes too, and the caller's claim follows from the callee's contract (`h() == 2`; CPython: 2).
"""
# pycsl-expected: PASS
from typing import Dict, Optional


#@ ensures \result == 1
#@ assigns \nothing
def g(x: int, d: Optional[Dict[str, str]] = None) -> int:
    return 1 if isinstance(d, dict) else 0


#@ ensures \result == 2
#@ assigns \nothing
def h() -> int:
    e: Dict[str, str] = {"a": "b"}
    y = g(3, e)
    return y + 1


if __name__ == "__main__":
    print("result", h())   # CPython: result 2
