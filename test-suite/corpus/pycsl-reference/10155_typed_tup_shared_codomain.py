r"""Test 10155 -- run #8 lvW typed tuple-return exception (expected PASS): two `Tuple[bool, str]` functions and one `Tuple[int, str]` function share ONE declared `exception Return_tup_int_string (int, string)` (bool is int in the value model); each catch is local to its own function, so the payloads do not leak. Twin: 10156 (expected FAIL).
"""
# pycsl-expected: PASS
from typing import Tuple

#@ requires True
#@ ensures \result[0] == True ==> \result[1] == ""
def f(x: int) -> Tuple[bool, str]:
    if x > 0:
        return True, ""
    return False, "neg"

#@ requires True
#@ ensures \result[0] == x and \result[1] == "a"
def g(x: int) -> Tuple[int, str]:
    if x > 0:
        return x, "a"
    return x, "a"

#@ requires True
#@ ensures \result[1] == "b"
def h(x: int) -> Tuple[bool, str]:
    if x > 0:
        return False, "b"
    return True, "b"


if __name__ == "__main__":
    print(f(1), f(0), g(2), g(-2), h(1), h(0))
