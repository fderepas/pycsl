r"""Test 10154 -- run #8 lvW typed tuple-return exception MUTANT (expected FAIL): 10153's in-loop return mutated to `return True, n`; the claim `\result[0] == True ==> \result[1] < n` is FALSE of the program (CPython: b_loop_bool_int(5) == (True, 5)) and must not prove.
"""
# pycsl-expected: FAIL
from typing import Tuple

#@ requires n >= 0
#@ ensures \result[0] == True ==> \result[1] < n
def b_loop_bool_int(n: int) -> Tuple[bool, int]:
    i = 0
    #@ loop invariant 0 <= i <= n
    #@ loop variant n - i
    while i < n:
        if i * i == 9:
            return True, n
        i += 1
    return False, n


if __name__ == "__main__":
    print(b_loop_bool_int(5), b_loop_bool_int(2))
