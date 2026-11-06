r"""Test 9126 -- run #5 lvJ empty-dict typing (expected FAIL): the 9125 program with the FALSE claim that membership is the argument's in both arms (`h({"a": "z"}, "a", 0)` returns 0).
"""
# pycsl-expected: FAIL
from typing import Dict, Set

#@ ensures \result == 1 <==> k in d
#@ assigns \nothing
def h(d: Dict[str, str], k: str, keep: int) -> int:
    y = {} if keep != 1 else d
    if k in y:
        return 1
    return 0

if __name__ == "__main__":
    print(h({"a": "z"}, "a", 1), h({"a": "z"}, "a", 0))
