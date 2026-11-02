r"""Test 8270 -- route #519 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 48 probe g920/d9000_strmul_init.py): `self.k = len("ab" * n)` in `__init__`; the constructor is lowered to a record literal and its body never judged; CPython raises OverflowError at f(10**20)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, n: int) -> None:
        self.k = len("ab" * n)


#@ no_exception \all
def f(n: int) -> int:
    c = C(n)
    return c.k


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", repr(r)[:40])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
