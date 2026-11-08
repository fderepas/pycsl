r"""Test 8627 -- route #547 (expected FAIL: PROVED at base int28, now REFUSED PYCSL-R490-LITERAL-INT-HASH; red team 52 probe g1323_bx1201_int_method): `Q().m(k) + 1` of an instance method `-> int` returning None; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    a: int


class Q:
    def __init__(self) -> None:
        self.a = 1

    def m(self, k: int) -> int:
        return None


#@ no_exception \all
def f(k: int) -> int:
    return Q().m(k) + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
