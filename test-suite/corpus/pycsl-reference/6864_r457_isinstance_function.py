r"""Test 6864 -- route #457 (expected FAIL): red team 36 witness `witnesses-r457/c23_i005.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): `isinstance(x, loads)` with `from json import loads`; CPython TypeError. Refused PYCSL-R457-CLASS-SPEC-NOT-A-CLASS.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

from json import loads



#@ no_exception \all
def f(x: int) -> int:
    if isinstance(x, loads):
        return 1
    return 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
