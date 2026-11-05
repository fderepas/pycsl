r"""Test 8896 -- route #562 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R562-COMPREHENSION-ELEMENT-KIND; u26 probe beyond red team 53's family): `return len({p < p for x in xs})`; CPython TypeError: '<' not supported between instances of 'P' and 'P'
"""
# pycsl-expected: FAIL
from typing import List
from dataclasses import dataclass


@dataclass
class P:
    a: int


#@ no_exception \all
def f(xs: List[int], p: P) -> int:
    return len({p < p for x in xs})


if __name__ == "__main__":
    try:
        print(f([1, 2], P(1)))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
