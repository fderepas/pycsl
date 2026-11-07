r"""Test 8718 -- route #552 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R552-VALUE-KIND-MISMATCH; red team 52 probe g1335/cj1200_range_file_arg.py): `h(range(k))` into `def h(x: int)` doing `x + 1`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass



def h(x: int) -> int:
    return x + 1


@dataclass
class R:
    a: int


#@ no_exception \all
def f(k: int, xs: List[int], d: Dict[str, int]) -> int:
    return h(range(k))


if __name__ == "__main__":
    try:
        r = f(1, [1], {"a": 1})
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
