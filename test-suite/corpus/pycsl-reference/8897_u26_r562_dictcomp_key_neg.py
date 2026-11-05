r"""Test 8897 -- route #562 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R562-COMPREHENSION-ELEMENT-KIND; u26 probe beyond red team 53's family): `return len({-t: x for x in xs})`; CPython TypeError: bad operand type for unary -: 'str'
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(xs: List[int], t: str) -> int:
    return len({-t: x for x in xs})


if __name__ == "__main__":
    try:
        print(f([1, 2], "ab"))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
