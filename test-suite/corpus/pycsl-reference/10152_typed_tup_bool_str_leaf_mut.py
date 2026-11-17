r"""Test 10152 -- run #8 lvW typed tuple-return exception MUTANT (expected FAIL): 10151 with the early `True` return's string mutated to "x"; the claim `\result[0] == True ==> \result[1] == ""` is FALSE of the program (CPython: f(1) == (True, "x")) and must not prove.
"""
# pycsl-expected: FAIL
from typing import Tuple

#@ requires True
#@ ensures \result[0] == True ==> \result[1] == ""
def f(x: int) -> Tuple[bool, str]:
    if x > 0:
        return True, "x"
    return False, "neg"


if __name__ == "__main__":
    print(f(1), f(-1))
