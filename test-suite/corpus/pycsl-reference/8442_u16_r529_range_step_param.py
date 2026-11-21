r"""Test 8442 -- route #529 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1100/ba1077_for_range_step_param.py): `range(0, 5, s)` with a parameter step in a constructor judged by route #519; CPython ValueError: range() arg 3 must not be zero
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, s: int) -> None:
        self.k = 0
        for i in range(0, 5, s):
            self.k = i


#@ no_exception \all
def f(s: int) -> int:
    c = C(s)
    return 1


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
