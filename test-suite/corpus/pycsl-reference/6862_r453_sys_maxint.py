r"""Test 6862 -- route #453 (expected FAIL): red team 36 witness `witnesses-r453/c21_a000_sys_maxint.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): `sys.maxint` (a Python 2 name) lowered as an opaque `get_maxint`; CPython AttributeError. Refused PYCSL-R453-MODULE-ATTRIBUTE.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

import sys



#@ no_exception \all
def f(n: int) -> int:
    y = sys.maxint
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
