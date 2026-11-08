r"""Test 8070 -- route #509 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R509-COMPREHENSION-OVERFLOW-SITE; red team 46 probe y7065_listrange_genexp_list): a generator element `list(range(n))` under `list(...)`; CPython f(10**20) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    v = list(list(range(n)) for _ in range(1))
    return 1


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
