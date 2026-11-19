r"""Test 9121 -- run #5 lvJ empty-dict typing (expected FAIL): the 9120 program with the FALSE claim that the rebind keeps the argument's entries (`f({"a": "z"}, "a", 1)` returns "").
"""
# pycsl-expected: FAIL
from typing import Dict, Set

#@ ensures (k in d) ==> \result == d[k]
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
