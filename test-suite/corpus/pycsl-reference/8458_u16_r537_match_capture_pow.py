r"""Test 8458 -- route #537 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1109/bj1041_mc_pow_str_init.py): `match s: case n:` then `n ** 2` in a constructor judged by route #519; CPython TypeError: unsupported operand type(s) for **
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, n: int, s: str) -> None:
        match s:
            case n:
                pass
        self.k = n ** 2


#@ no_exception \all
def f(n: int, s: str) -> int:
    c = C(n, s)
    return 1


if __name__ == "__main__":
    try:
        r = f(5, "a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
