r"""Test 6859 -- route #446 (expected FAIL): red team 36 witness `witnesses-r446/c4_a047_augelem_7.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): `xs[0] @= b`; CPython TypeError. Refused PYCSL-R446-MATMUL-UNMODELLED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
#@ assigns xs
def f(xs: List[int], b: int) -> int:
    if not xs:
        return 0
    xs[0] @= b
    return 1


if __name__ == "__main__":
    try:
        r = f([1], 2)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
