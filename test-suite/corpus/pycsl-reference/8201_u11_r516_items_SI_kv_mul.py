r"""Test 8201 -- route #516 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R507-OVERFLOW-SITE-UNLOWERED; red team 47 probe g819/w8024_SI_kv_mul_items): `for k, v in d.items(): w = k * v` over `Dict[str, int]` (str repetition by an erased int); CPython f({"ab": 10**20}) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    for k, v in d.items():
        w = k * v
    return 1


if __name__ == "__main__":
    try:
        r = f({"ab": 10**20})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
