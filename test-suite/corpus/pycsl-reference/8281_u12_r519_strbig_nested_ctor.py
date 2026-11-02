r"""Test 8281 -- route #519 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 48 probe g921/e9016_strbig_nested_ctor.py): a nested constructor whose `__init__` holds `str(n)`; the constructor is lowered to a record literal and its body never judged; CPython raises ValueError (4300 digits)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, n: int) -> None:
        self.k = str(n)


class D:
    def __init__(self, n: int) -> None:
        self.c = C(n)


class Mk:
    def build(self, n: int) -> int:
        c = C(n)
        return 1


@dataclass
class P:
    c: C


#@ no_exception \all
def f(n: int) -> int:
    d = D(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(10**5000)
        print("result", repr(r)[:40])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
