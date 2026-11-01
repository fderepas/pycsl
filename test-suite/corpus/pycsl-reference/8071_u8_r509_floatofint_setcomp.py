r"""Test 8071 -- route #509 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R509-COMPREHENSION-OVERFLOW-SITE; red team 46 probe y7101_floatofint_setcomp): a set comprehension element `float(n)` (route #417's |n| <= DBL_MAX); CPython f(10**400) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    v = {float(n) for _ in range(1)}
    return 1


if __name__ == "__main__":
    try:
        r = f(10**400)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
