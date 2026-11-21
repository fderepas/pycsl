r"""Test 9125 -- run #5 lvJ empty-dict typing (expected PASS): the mirrored IfExp (`{} if c else d`, the empty arm FIRST, unannotated target): membership of the empty arm is False.
"""
# pycsl-expected: PASS
from typing import Dict, Set

#@ ensures keep != 1 ==> \result == 0
#@ ensures keep == 1 ==> (\result == 1 <==> k in d)
#@ assigns \nothing
def h(d: Dict[str, str], k: str, keep: int) -> int:
    y = {} if keep != 1 else d
    if k in y:
        return 1
    return 0

if __name__ == "__main__":
    print(h({"a": "z"}, "a", 1), h({"a": "z"}, "a", 0))
