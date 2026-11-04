r"""Test 8628 -- route #547 (expected FAIL: PROVED at base int28, now REFUSED PYCSL-R490-LITERAL-INT-HASH; red team 52 probe g1315_bp1226_self_call): `self.m() + 1` of a `-> int` staticmethod returning None, reached through `Q().g()`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class Q:
    def __init__(self) -> None:
        self.a = 1

    @staticmethod
    def m() -> int:
        return None

    def g(self) -> int:
        return self.m() + 1


#@ no_exception \all
def f(k: int) -> int:
    return Q().g()


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
