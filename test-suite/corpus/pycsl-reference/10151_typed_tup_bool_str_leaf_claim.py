r"""Test 10151 -- run #8 lvW typed tuple-return exception (expected PASS): the typed payload carries the real string, so `\result[0] == True ==> \result[1] == ""` proves through the early `Return_tup_int_string` raise. Twin: 10152 (expected FAIL).
"""
# pycsl-expected: PASS
from typing import Tuple

#@ requires True
#@ ensures \result[0] == True ==> \result[1] == ""
def f(x: int) -> Tuple[bool, str]:
    if x > 0:
        return True, ""
    return False, "neg"


if __name__ == "__main__":
    print(f(1), f(-1))
