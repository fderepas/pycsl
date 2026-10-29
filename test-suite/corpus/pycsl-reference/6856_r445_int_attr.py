r"""Test 6856 -- route #445 (expected FAIL): red team 36 witness `witnesses-r445/c42_a000.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): `n.zz` on an `int`; CPython AttributeError. Refused PYCSL-R445-ATTRIBUTE-NOT-DEFINED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    y = n.zz
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
