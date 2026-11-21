r"""Test 6870 -- route #444 (expected PASS): CONTROL -- every name read resolves: a module-level constant `K`, a builtin (`len`), a parameter and locals. Not refused by PYCSL-R444-UNBOUND-NAME.
"""
# pycsl-expected: PASS
from typing import List

K = 3


#@ no_exception \all
#@ ensures \result == 3 + len(xs)
def f(xs: List[int]) -> int:
    total = K
    n = len(xs)
    return total + n


if __name__ == "__main__":
    print("result", f([1, 2]), f([]))
