r"""Test 6858 -- route #446 (expected FAIL): red team 36 witness `witnesses-r446/c1_o048_matmul.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): `a @ b` on ints lowered as `unknown_op`; CPython TypeError. Refused PYCSL-R446-MATMUL-UNMODELLED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(a: int, b: int) -> int:
    return a @ b


if __name__ == "__main__":
    try:
        r = f(1, 2)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
