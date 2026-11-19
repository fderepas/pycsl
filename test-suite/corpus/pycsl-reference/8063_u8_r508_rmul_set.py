r"""Test 8063 -- route #508 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R508-INT-FLOAT-PROMOTION-UNMODELLED; red team 46 probe u7025_rmul_set): `{0.5 * n}`: the int -> float promotion has no obligation; CPython raises OverflowError for n = 10**400
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int, x: float) -> int:
    v = {0.5 * n}
    return 1


if __name__ == "__main__":
    try:
        r = f(10**400, 0.5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
