r"""Test 8064 -- route #508 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R508-INT-FLOAT-PROMOTION-UNMODELLED; red team 46 probe u7041_x_plus_n_set): `{x + n}` with x: float, n: int: the int -> float promotion has no obligation; CPython f(10**400, 0.5) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int, x: float) -> int:
    v = {x + n}
    return 1


if __name__ == "__main__":
    try:
        r = f(10**400, 0.5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
