r"""Test 4394 -- gen #37 route #332 (expected PASS): CONTROL: a TRUE assert with an effectful message (`assert x == 2, xs.pop()`) under `no_exception \all` PROVES: the message is never evaluated.
"""
# pycsl-expected: PASS
from typing import List
#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception \all
def g(xs: List[int]) -> int:
    x = 2
    assert x == 2, xs.pop()
    return 7

if __name__ == "__main__":
    try:
        print(g([]))
    except AssertionError:
        print("CPython raises AssertionError")
