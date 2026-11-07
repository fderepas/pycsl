r"""Test 8717 -- route #552 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R552-VALUE-KIND-MISMATCH; red team 52 probe g1322/bw1251_keys_lt.py): `d.keys() < 3`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, xs: List[int], d: Dict[str, int]) -> int:
    return 1 if d.keys() < 3 else 0


if __name__ == "__main__":
    try:
        r = f(1, [1], {"a": 1})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
