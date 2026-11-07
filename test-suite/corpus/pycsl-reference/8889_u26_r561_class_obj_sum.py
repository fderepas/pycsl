r"""Test 8889 -- route #561 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R561-COMPREHENSION-NON-ITERABLE-OPERAND; u26 probe beyond red team 53's family): `return sum(1 for x in KI)`; CPython TypeError: 'type' object is not iterable
"""
# pycsl-expected: FAIL
from typing import List


class KI:
    def __init__(self, a: int) -> None:
        self.a = a


#@ no_exception \all
def f(k: int) -> int:
    return sum(1 for x in KI)


if __name__ == "__main__":
    try:
        print(f(1))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
