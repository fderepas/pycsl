r"""Test 8462 -- route #539 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1106/bg1028_ctor_global_none_add.py): `n + Z` with the module global `Z = None` in a constructor judged by route #519; CPython TypeError: unsupported operand
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses
Z = None


class P:
    def __init__(self, n: int) -> None:
        self.a = n
        self.k = n + Z


#@ no_exception \all
def f(n: int) -> int:
    p = P(n)
    return p.a


if __name__ == "__main__":
    try:
        r = f(5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
