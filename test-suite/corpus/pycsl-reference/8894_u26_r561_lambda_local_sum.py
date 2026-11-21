r"""Test 8894 -- route #561 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R561-COMPREHENSION-NON-ITERABLE-OPERAND; u26 probe beyond red team 53's family): `g = lambda: 1; return sum(1 for x in g)`; CPython TypeError: 'function' object is not iterable
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(k: int) -> int:
    g = lambda: 1
    return sum(1 for x in g)


if __name__ == "__main__":
    try:
        print(f(1))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
