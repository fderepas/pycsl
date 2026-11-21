r"""Test 9171 -- route #571 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R571-ENUM-MEMBER-NAME-KIND; a new false proof beyond red team 54's family, measured PROVED at base 8358d5d31): `n = IE.A.name; return n + 1`; CPython TypeError: can only concatenate str (not "int") to str
"""
# pycsl-expected: FAIL
from typing import Any, List, Tuple
import enum
class IE(enum.IntEnum):
    A = 1
    B = 2

#@ no_exception \all
def f(k: int) -> int:
    n = IE.A.name
    return n + 1

if __name__ == "__main__":
    print(f(1))
