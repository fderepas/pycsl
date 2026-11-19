r"""Test 9912 -- lvS Optional-list arm CONTROL (expected PASS): the Some arm of a verified `->
Optional[List[str]]` function is the list's `seq string` VALUE (was the int-erased `Arm_i_0 int`,
against which `return out` was a Why3 type error), and `return out` injects `!out` into it, on the
early (`raise Return_<variant>`) path too. Twin: 9913 (must FAIL).
"""
# pycsl-expected: PASS
from typing import List, Optional


#@ assigns \nothing
def nonempty(xs: List[str]) -> Optional[List[str]]:
    out: List[str] = []
    for i in range(len(xs)):
        x: str = xs[i]
        if x == "":
            return None
        out.append(x)
    return out


if __name__ == "__main__":
    print("result", nonempty(["a", "b"]), nonempty(["a", ""]))
