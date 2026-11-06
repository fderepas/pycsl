r"""Test 9127 -- run #5 lvJ empty-dict typing (expected FAIL): CONTROL: a `{}` arm beside a SET-typed arm is NOT typed from it (`{}` is a dict, not a set): the emission stays the base's ill-typed int arm (fail-closed).
"""
# pycsl-expected: FAIL
from typing import Dict, Set

#@ ensures keep != 1 ==> \result == 0
#@ assigns \nothing
def s(xs: Set[int], keep: int) -> int:
    y = xs if keep == 1 else {}
    if 3 in y:
        return 1
    return 0

if __name__ == "__main__":
    print(s({3}, 1), s({3}, 0))
