r"""Test 8074 -- route #508 / #509 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R508-INT-FLOAT-PROMOTION-UNMODELLED; red team 46 probe y7080_intfloat_listcomp): a list comprehension element `n * 1.5` -- the int -> float promotion has no obligation and is refused wherever it occurs; CPython f(10**400) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    v = [n * 1.5 for _ in range(1)]
    return 1


if __name__ == "__main__":
    try:
        r = f(10**400)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
