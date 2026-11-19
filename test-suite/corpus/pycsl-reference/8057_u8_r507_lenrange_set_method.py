r"""Test 8057 -- route #507 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R507-OVERFLOW-SITE-UNLOWERED; red team 46 probe t7149_lenrange_set_method): a method evaluates `{len(range(self.n))}` under `no_exception \all`; CPython f(10**20) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class K:
    def __init__(self, n: int) -> None:
        self.n = n

    #@ no_exception \all
    def m(self) -> int:
        v = {len(range(self.n))}
        return 1


#@ no_exception \all
def f(n: int) -> int:
    k = K(n)
    return k.m()


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
