r"""Test 8867 -- route #561 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R561-COMPREHENSION-NON-ITERABLE-OPERAND; red team 53 probe g1423/dx1227_h_fn_sum.py): `return sum(1 for x in h)`; CPython TypeError: 'function' object is not iterable
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
    return sum(1 for x in h)


if __name__ == "__main__":
    try:
        r = f(1, P(1))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
