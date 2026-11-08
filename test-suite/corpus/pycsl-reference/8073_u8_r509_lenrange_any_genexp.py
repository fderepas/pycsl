r"""Test 8073 -- route #509 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R509-COMPREHENSION-OVERFLOW-SITE; red team 46 probe z7011_lenrange_any_genexp): the iterable `[len(range(n))]` of a generator under `any(...)`; CPython f(10**20) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    if any(True for _ in [len(range(n))]):
        return 1
    return 0


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
