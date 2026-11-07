r"""Test 6852 -- route #444 (expected FAIL): red team 36 witness `witnesses-r444/c4_n009_global_defined_later.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): an undefined global `LATE`; CPython NameError. Refused PYCSL-R444-UNBOUND-NAME.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(a: int) -> int:
    return a + LATE


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
