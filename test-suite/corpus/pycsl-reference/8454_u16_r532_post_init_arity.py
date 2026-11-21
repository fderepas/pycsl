r"""Test 8454 -- route #532 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1101/bb1039_dc_post_init_extra_param.py): a dataclass `__post_init__(self, m)` with no InitVar in a constructor judged by route #519; CPython TypeError: missing 1 required positional argument
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class C:
    a: int

    def __post_init__(self, m: int) -> None:
        self.k = m


#@ no_exception \all
def f(n: int) -> int:
    c = C(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
