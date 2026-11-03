r"""Test 8338 -- route #524 (expected FAIL: PROVED at base 1aaa1dfdd, NOT PROVED on the PyCSL-R521 None obligation; red team 49 probe ab1001_ll_opt_str_len_concat): `xss[0][0] + "x"` of List[List[Optional[str]]]; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires len(xss) >= 1 and len(xss[0]) >= 1
#@ no_exception \all
def f(xss: List[List[Optional[str]]]) -> int:
    v = xss[0][0] + "x"
    return 1


if __name__ == "__main__":
    try:
        r = f([[None]])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
