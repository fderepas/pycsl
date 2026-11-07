r"""Test 8335 -- route #524 (expected FAIL: PROVED at base 1aaa1dfdd, NOT PROVED on the PyCSL-R521 None obligation; red team 49 probe y1000_ll_add): `xss[0][0] + 1` of List[List[Optional[int]]]; CPython f([[None]]) TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires len(xss) >= 1 and len(xss[0]) >= 1
#@ no_exception \all
def f(xss: List[List[Optional[int]]]) -> int:
    return xss[0][0] + 1


if __name__ == "__main__":
    try:
        r = f([[None]])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
