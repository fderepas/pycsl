r"""Test 7032 -- route #456 (expected FAIL): red-team 36 probe c22_v010_tuple_values -- `s.difference(d.values())` with `Tuple[List[int], int]` values (CPython TypeError). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(s: Set[int], d: Dict[int, Tuple[List[int], int]]) -> int:
    return len(s.difference(d.values()))


if __name__ == "__main__":
    try:
        r = f({1}, {1: ([1], 2)})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
