r"""Test 10054 -- lvU none-default map parameter `x or {}` (expected FAIL): an EXPLICIT `None`
argument is not a map (it lowers to the opaque int `pycsl_none`, a Why3 type error against the map
parameter: fail-closed at L3-tc), so the map model of `d or {}` never sees CPython's `None`. CPython:
`caller()` is 0, so `\result == 5` is also false. Control: 10050.
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
    return g("a", None)


if __name__ == "__main__":
    r = caller()
    print("VIOLATION contract" if r != 5 else "result", r)
