r"""Test 10053 -- lvU none-default map parameter `x or {}` (expected FAIL): a caller that OMITS the
argument never reaches the map model of `d or {}` with CPython's `None`: here the call-site default
fill types this parameter `int` and fills `0`, a Why3 type error against the map (L3-tc, fail
closed); where the fill is the opaque `pycsl_none_map`, route #592 refuses it at the call of a
VERIFIED callee (PYCSL-R592-NONE-DEFAULT-MAP-CONCRETE). CPython: `g("a")` is 0, so `\result == 5` is
also false. Control: 10050.
"""
# pycsl-expected: FAIL
from typing import Dict, Optional


#@ ensures \result >= 0
#@ assigns \nothing
def g(k: str, d: Optional[Dict[str, int]] = None) -> int:
    d = d or {}
    v = d.get(k, 0)
    if v < 0:
        return 0
    return v


#@ ensures \result == 5
#@ assigns \nothing
def caller() -> int:
    return g("a")


if __name__ == "__main__":
    r = caller()
    print("VIOLATION contract" if r != 5 else "result", r)
