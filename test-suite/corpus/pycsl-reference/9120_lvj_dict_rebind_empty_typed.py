r"""Test 9120 -- run #5 lvJ empty-dict typing (expected PASS): an annotated `Dict[str, str]` local REBOUND to `{}` is the string-valued empty map (base: the int-typed empty map, L3-tc failure).
"""
# pycsl-expected: PASS
from typing import Dict, Set

#@ ensures mode == 1 ==> \result == ""
#@ ensures (mode != 1 and k in d) ==> \result == d[k]
#@ ensures (mode != 1 and not (k in d)) ==> \result == ""
#@ assigns \nothing
def f(d: Dict[str, str], k: str, mode: int) -> str:
    x: Dict[str, str] = d
    if mode == 1:
        x = {}
    if k in x:
        return x[k]
    return ""

if __name__ == "__main__":
    print(repr(f({"a": "z"}, "a", 1)), repr(f({"a": "z"}, "a", 0)))
