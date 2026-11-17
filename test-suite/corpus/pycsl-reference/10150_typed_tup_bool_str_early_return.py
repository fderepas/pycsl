r"""Test 10150 -- run #8 lvW typed tuple-return exception (expected PASS): a `Tuple[bool, str]` early return raises its own payload-typed `Return_tup_int_string`, an all-int `Tuple[int, int]` keeps `Return_2`, and an in-loop `Tuple[int, str]` return carries `\result[0] == x`. At base 0057c8b94 `f` was an L3-tc rejection (`(int, string)` vs the shared `Return_2 (int, int)`).
"""
# pycsl-expected: PASS
from typing import Tuple

#@ ensures \result[0] == True ==> x > 0
def f(x: int) -> Tuple[bool, str]:
    if x > 0:
        return True, ""
    return False, "neg"

#@ ensures x > 0 ==> \result[0] + \result[1] == 3
def g(x: int) -> Tuple[int, int]:
    if x > 0:
        return 1, 2
    return 3, 4

#@ ensures \result[0] == x
def h(x: int) -> Tuple[int, str]:
    i = 0
    #@ loop invariant 0 <= i <= 3
    #@ loop variant 3 - i
    while i < 3:
        if i == x:
            return x, "hit"
        i += 1
    return x, "miss"


if __name__ == "__main__":
    print(f(1), f(-1), g(1), g(0), h(1), h(7))
