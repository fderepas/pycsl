r"""Test 8866 -- route #561 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R561-COMPREHENSION-NON-ITERABLE-OPERAND; red team 53 probe g1423/dx1218_ki_local_sum.py): `w = KI(k); return sum(1 for x in w)`; CPython TypeError: 'KI' object is not iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int


class KI:
    def __init__(self, a: int) -> None:
        self.a = a


def h(x: int) -> int:
    return x + 1



#@ no_exception \all
def f(k: int, p: P) -> int:
    w = KI(k)
    return sum(1 for x in w)


if __name__ == "__main__":
    try:
        r = f(1, P(1))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
