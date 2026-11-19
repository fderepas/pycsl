r"""Test 8278 -- route #519 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 48 probe g920/d9140_sorted_mixed_init.py): `self.k = len(sorted([n, "a"]))` in `__init__`; the constructor is lowered to a record literal and its body never judged; CPython raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, n: int) -> None:
        self.k = len(sorted([n, "a"]))


#@ no_exception \all
def f(n: int) -> int:
    c = C(n)
    return c.k


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:40])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
