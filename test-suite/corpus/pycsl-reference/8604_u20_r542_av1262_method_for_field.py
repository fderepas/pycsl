r"""Test 8604 -- route #542 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R542-NON-CONTAINER-OPERAND; red team 51 probe g1243/av1262_method_for_field.py): a method iterates its int field `self.n`; CPython f(3) -> TypeError 'int' object is not iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    a: int
    s: str


def two() -> int:
    return 2


class M:
    def __init__(self, n: int) -> None:
        self.n = n

    #@ no_exception \all
    def m(self) -> int:
        c2 = 0
        for c in self.n:
            c2 += 1
        return c2



#@ no_exception \all
def f(k: int) -> int:
    return M(k).m()


if __name__ == "__main__":
    try:
        r = f(3)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
