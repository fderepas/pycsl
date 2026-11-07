r"""Test 3304 -- route #283 (expected FAIL): census: the FRESH `b = [0] * 3` is not seq-promoted either, so `b.append(9); len(b) == 1` PROVED (counter at 0); CPython: 4.
Now refused (PYCSL-WHYML-APPEND-UNTRACKED-LIST).
"""
# pycsl-expected: FAIL
from typing import List


#@ assigns \nothing
def ident(x: List[int]) -> List[int]:
    return x


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    b = [0] * 3
    b.append(9)
    return len(b)


if __name__ == "__main__":
    assert f() == 4
