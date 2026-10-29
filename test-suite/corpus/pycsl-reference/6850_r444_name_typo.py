r"""Test 6850 -- route #444 (expected FAIL): red team 36 witness `witnesses-r444/c11_q021_realistic_typo.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): a misspelt local (`totl` for `total`) lowered as an opaque `val constant`; CPython NameError. Refused PYCSL-R444-UNBOUND-NAME.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(items: List[int]) -> int:
    total = 0
    for it in items:
        total += it
    return totl


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
