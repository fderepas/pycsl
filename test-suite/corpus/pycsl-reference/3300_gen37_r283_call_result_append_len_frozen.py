r"""Test 3300 -- route #283 (expected FAIL): red-team p143: `b = ident([5]); b.append(9); len(b)` -- the counter `b_len` started at 0, so `\result == 1` PROVED; CPython: 2.
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
    b = ident([5])
    b.append(9)
    return len(b)


if __name__ == "__main__":
    assert f() == 2
