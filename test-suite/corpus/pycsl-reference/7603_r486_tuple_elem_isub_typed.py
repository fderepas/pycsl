r"""Test 7603 -- route #486 (expected FAIL): red-team 40 probe g107_e10702_tuple_elem_isub under `--memory-model typed` -- `a[0] -= 1` on `a: List[Tuple[int, int]]` (CPython TypeError) PROVED at base 0c61bfc3f; now REFUSED (PYCSL-R486-NONSCALAR-AUGASSIGN-TARGET).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ requires len(a) == 1
#@ no_exception \all
def f(a: List[Tuple[int, int]]) -> int:
    a[0] -= 1
    return 0


if __name__ == "__main__":
    try:
        r = f([(1, 2)])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
