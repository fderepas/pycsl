r"""Test 10055 -- lvU none-default map parameter `x or {}` (expected FAIL): `d` is MUTATED after
`d = d or {}`. For an empty caller dict CPython mutates the FRESH `{}` (the caller's dict stays
empty), for a non-empty one it mutates the caller's: the identity difference is observable, so the
arm is closed for a caller-visible mutated parameter and the old lowering (an int `or` over the map,
a Why3 type error) stays. CPython: `caller()` is 0, so `\result == 1` is false. Control: 10050.
"""
# pycsl-expected: FAIL
from typing import Dict, Optional


#@ ensures \result >= 0
def put(d: Optional[Dict[str, int]] = None) -> int:
    d = d or {}
    d["a"] = 1
    return 0


#@ ensures \result == 1
def caller() -> int:
    m: Dict[str, int] = {}
    put(m)
    if "a" in m:
        return 1
    return 0


if __name__ == "__main__":
    r = caller()
    print("VIOLATION contract" if r != 1 else "result", r)
