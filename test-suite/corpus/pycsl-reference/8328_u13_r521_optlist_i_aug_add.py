r"""Test 8328 -- route #521 (expected FAIL: PROVED at base 1aaa1dfdd, NOT PROVED on the PyCSL-R521 None obligation; red team 49 probe af1007_optlist_i_aug_add): `t += xs[0]` of List[Optional[int]]; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires len(xs) >= 1
#@ no_exception \all
def f(xs: List[Optional[int]]) -> int:
    t = 1
    t += xs[0]
    return t


if __name__ == "__main__":
    try:
        r = f([None])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
