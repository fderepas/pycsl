r"""Test 9124 -- run #5 lvJ empty-dict typing (expected FAIL): the 9123 program with the FALSE claim that the `{}` arm keeps the argument's entries (`g({"a": "z"}, "a", 0)` returns "").
"""
# pycsl-expected: FAIL
from typing import Dict, Set

#@ ensures (k in d) ==> \result == d[k]
#@ assigns \nothing
def g(d: Dict[str, str], k: str, keep: int) -> str:
    y: Dict[str, str] = d if keep == 1 else {}
    if k in y:
        return y[k]
    return ""

if __name__ == "__main__":
    print(repr(g({"a": "z"}, "a", 1)), repr(g({"a": "z"}, "a", 0)))
