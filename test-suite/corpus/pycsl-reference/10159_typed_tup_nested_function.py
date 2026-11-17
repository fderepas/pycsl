r"""Test 10159 -- run #8 lvW typed tuple-return exception (expected PASS): a NESTED function returning `Tuple[bool, str]` with early `Return_tup_int_string` raises; the outer claim `x > 0 ==> \result == 1` proves through the nested contract `y > 0 ==> \result[0] == True`. (Its mutant, nested `True` mutated to `False`, FAILS: scratchpad/lvW/rt.)
"""
# pycsl-expected: PASS
from typing import Tuple

#@ ensures x > 0 ==> \result == 1
def outer(x: int) -> int:
    #@ ensures y > 0 ==> \result[0] == True
    def inner(y: int) -> Tuple[bool, str]:
        if y > 0:
            return True, ""
        return False, "n"
    t = inner(x)
    if t[0]:
        return 1
    return 0


if __name__ == "__main__":
    print(outer(1), outer(0))
