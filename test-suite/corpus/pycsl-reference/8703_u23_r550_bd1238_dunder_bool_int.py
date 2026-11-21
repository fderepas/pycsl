r"""Test 8703 -- route #550 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 52 probe g1303/bd1238_dunder_bool_int.py): a constructor tests `Bo()` whose `__bool__` returns 2; CPython TypeError: __bool__ should return bool, returned int
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class Bo:
    def __bool__(self):
        return 2


class C:
    def __init__(self, n: int) -> None:
        self.b = 1 if Bo() else 0


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
