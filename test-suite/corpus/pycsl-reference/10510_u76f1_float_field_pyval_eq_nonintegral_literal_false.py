r"""Test 10510 -- run #9 u76, review rt84 F1 (u74 link-1 float-field PyVal carrier). A float record field stored in a
Dict[str, PyVal] and compared with the non-integral literal 1.5: `cd <tree root> && python <this file>` prints
"result 0", so the claim below is false. u74 head PROVED it (the field was the erased `HInt` carrier, which the
float-literal equality arm answers `false`); L21 failed closed at Why3 type-check. Now the field is the faithful
`HFloat x` (or, when integral, `HInt i`), the equality is decided as CPython decides it: VERIFY-FAIL.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Any, Dict

PyVal = Any


@dataclass
class R:
    x: float


#@ ensures \result == 1
#@ assigns \nothing
def f(r: R) -> int:
    d: Dict[str, PyVal] = {"a": r.x}
    if d.get("a") == 1.5:
        return 0
    return 1


if __name__ == "__main__":
    print("result", f(R(1.5)))
