r"""Test 8895 -- route #562 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R562-COMPREHENSION-ELEMENT-KIND; u26 probe beyond red team 53's family): `return sum(h(x, y=t) for x in xs)`; CPython TypeError: unsupported operand type(s) for +: 'int' and 'str'
"""
# pycsl-expected: FAIL
from typing import List


def h(x: int, y: int = 0) -> int:
    return x + y


#@ no_exception \all
def f(xs: List[int], t: str) -> int:
    return sum(h(x, y=t) for x in xs)


if __name__ == "__main__":
    try:
        print(f([1, 2], "ab"))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
