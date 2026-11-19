r"""Test 8708 -- route #550 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 52 probe g1313/bn1228_e_iter_any.py): `any(It())` in a constructor, `__iter__` returning 5; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class It:
    def __iter__(self):
        return 5


class C:
    def __init__(self, n: int) -> None:
        self.b = any(It())


#@ no_exception \all
def f(k: int) -> int:
    c = C(k)
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
