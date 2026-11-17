r"""Test 10153 -- run #8 lvW typed tuple-return exception (expected PASS): `(str, int)` -> `Return_tup_string_int`, an in-loop `(bool, int)` (all-int in the value model) -> `Return_2`, a 3-tuple `(int, str, int)` -> `Return_tup_int_string_int`, and an all-int `(int, int)` -> `Return_2`, each with a claim over the carried slots. Twin: 10154 (expected FAIL).
"""
# pycsl-expected: PASS
from typing import List, Tuple

#@ ensures \result[1] == len(s)
def a_str_int(s: str) -> Tuple[str, int]:
    if len(s) == 0:
        return "empty", 0
    return s, len(s)

#@ requires n >= 0
#@ ensures \result[0] == True ==> \result[1] < n
def b_loop_bool_int(n: int) -> Tuple[bool, int]:
    i = 0
    #@ loop invariant 0 <= i <= n
    #@ loop variant n - i
    while i < n:
        if i * i == 9:
            return True, i
        i += 1
    return False, n

#@ ensures \result[2] == x
def c_three(x: int) -> Tuple[int, str, int]:
    if x > 0:
        return 1, "pos", x
    return 0, "nonpos", x

#@ ensures \result[0] + \result[1] == 3
def d_all_int(x: int) -> Tuple[int, int]:
    if x > 0:
        return 1, 2
    return 2, 1


if __name__ == "__main__":
    print(a_str_int(""), a_str_int("ab"), b_loop_bool_int(5), b_loop_bool_int(2), c_three(4), d_all_int(0))
