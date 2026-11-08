r"""Test 9123 -- run #5 lvJ empty-dict typing (expected PASS): an IfExp whose `{}` arm sits beside a dict-typed arm: the arm is the empty map of the SIBLING's type (base: `(any int)`, L3-tc failure).
"""
# pycsl-expected: PASS
from typing import Dict, Set

#@ ensures keep != 1 ==> \result == ""
#@ ensures (keep == 1 and k in d) ==> \result == d[k]
#@ ensures (keep == 1 and not (k in d)) ==> \result == ""
#@ assigns \nothing
def g(d: Dict[str, str], k: str, keep: int) -> str:
    y: Dict[str, str] = d if keep == 1 else {}
    if k in y:
        return y[k]
    return ""

if __name__ == "__main__":
    print(repr(g({"a": "z"}, "a", 1)), repr(g({"a": "z"}, "a", 0)))
