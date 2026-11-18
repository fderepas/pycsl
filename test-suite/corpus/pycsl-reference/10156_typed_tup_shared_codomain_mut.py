r"""Test 10156 -- run #8 lvW typed tuple-return exception MUTANT (expected FAIL): 10155 with `g`'s early return string mutated to "z"; the claim `\result[0] == x and \result[1] == "a"` is FALSE of the program (CPython: g(2) == (2, "z")) and must not prove.
"""
# pycsl-expected: FAIL
from typing import Tuple

#@ ensures \result[0] == True ==> \result[1] == ""
def f(x: int) -> Tuple[bool, str]:
    if x > 0:
        return True, ""
    return False, "neg"

#@ ensures \result[0] == x and \result[1] == "a"
def g(x: int) -> Tuple[int, str]:
    if x > 0:
        return x, "z"
    return x, "a"

#@ ensures \result[1] == "b"
def h(x: int) -> Tuple[bool, str]:
    if x > 0:
        return False, "b"
    return True, "b"


if __name__ == "__main__":
    print(f(1), f(0), g(2), g(-2), h(1), h(0))
