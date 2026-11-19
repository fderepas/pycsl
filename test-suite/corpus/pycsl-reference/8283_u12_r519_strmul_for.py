r"""Test 8283 -- route #519 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 48 probe g925/j9015_strmul_for.py): `len("ab" * i)` in a `for` body of `__init__`; the constructor is lowered to a record literal and its body never judged; CPython raises OverflowError at f(10**20)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class Bad(Exception):
    pass


class C:
    def __init__(self, n: int) -> None:
        self.k = 0
        for i in [n]:
            self.k = len("ab" * i)


#@ no_exception \all
def f(n: int) -> int:
    c = C(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
