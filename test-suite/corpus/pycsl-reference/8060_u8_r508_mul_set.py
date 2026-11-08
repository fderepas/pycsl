r"""Test 8060 -- route #508 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R508-INT-FLOAT-PROMOTION-UNMODELLED; red team 46 probe u7001_mul_set): `{n * 1.5}`: the int -> float promotion of n has no obligation (OverflowError past DBL_MAX); CPython f(10**400, 0.5) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int, x: float) -> int:
    v = {n * 1.5}
    return 1


if __name__ == "__main__":
    try:
        r = f(10**400, 0.5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
