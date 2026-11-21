r"""Test 3301 -- route #283 (expected FAIL): red-team p130: the append stored at `b[!b_len]` = b[0] of the RETURNED array, so `b[0] == 9` PROVED; CPython: 5.
Now refused (PYCSL-WHYML-APPEND-UNTRACKED-LIST).
"""
# pycsl-expected: FAIL
from typing import List


#@ assigns \nothing
def ident(x: List[int]) -> List[int]:
    return x


#@ ensures \result == 9
#@ assigns \nothing
def f() -> int:
    b = ident([5])
    b.append(9)
    return b[0]


if __name__ == "__main__":
    assert f() == 5
