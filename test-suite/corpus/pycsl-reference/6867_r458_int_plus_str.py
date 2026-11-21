r"""Test 6867 -- route #458 (expected FAIL): red team 36 witness `witnesses-r458/c27_o010.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): `n + s` (int + str) lowered as a string concatenation; CPython TypeError. Refused PYCSL-R458-OPERAND-CLASSES.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(n: int, s: str) -> int:
    return n + s


if __name__ == "__main__":
    try:
        r = f(1, 'a')
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
