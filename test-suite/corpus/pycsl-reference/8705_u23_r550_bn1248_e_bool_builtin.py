r"""Test 8705 -- route #550 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 52 probe g1313/bn1248_e_bool_builtin.py): `bool(Bo())` in a constructor, `__bool__` returning 2; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class Bo:
    def __bool__(self):
        return 2


class C:
    def __init__(self, n: int) -> None:
        self.b = bool(Bo())


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
