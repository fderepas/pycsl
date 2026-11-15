r"""Test 9913 -- lvS Optional-list arm (expected FAIL): `return out` is the Some arm carrying the real
list, so `\result is None` is FALSE for an input without "" (CPython: ["a", "b"]) and must NOT prove.
Control: 9912.
"""
# pycsl-expected: FAIL
from typing import List, Optional


#@ ensures \result == None
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
    r = nonempty(["a", "b"])
    print("VIOLATION contract" if r is not None else "result", r)
