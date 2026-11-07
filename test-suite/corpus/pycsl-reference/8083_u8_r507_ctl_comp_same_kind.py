r"""Test 8083 -- routes #507 / #508 / #509 (control, expected PASS): comprehensions multiplying two ints of a `List[int]` and a float by a float literal (source annotations read through the erased symbol table); CPython f(5, [10**30, 2]) returns 1
"""
# pycsl-expected: PASS
from typing import List


#@ no_exception \all
#@ ensures \result == 1
def f(n: int, xs: List[int]) -> int:
    zs = {k * j for k in xs for j in xs}
    ws = [x * 0.5 for x in [1.5, 2.5]]
    return 1
