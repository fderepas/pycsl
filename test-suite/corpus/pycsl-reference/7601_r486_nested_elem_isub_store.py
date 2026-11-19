r"""Test 7601 -- route #486 (expected FAIL): red-team 40 probe g85_m8908_nested_elem_isub under `--memory-model store` -- `a[0] -= 1` on `a: List[List[int]]` (CPython TypeError list -= int) PROVED at base 0c61bfc3f; now REFUSED (PYCSL-R486-NONSCALAR-AUGASSIGN-TARGET).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model store
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ requires len(a) == 1
#@ no_exception \all
def f(a: List[List[int]]) -> int:
    a[0] -= 1
    return 0


if __name__ == "__main__":
    try:
        r = f([[0]])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
