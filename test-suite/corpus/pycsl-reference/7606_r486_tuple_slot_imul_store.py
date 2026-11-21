r"""Test 7606 -- route #486 (expected FAIL): red-team 40 probe g85_m8907_tuple_elem_imul under `--memory-model store` -- `t[0] *= 2` on `t: Tuple[List[int], int]` (CPython TypeError: a tuple is not item-assignable) PROVED at base 0c61bfc3f; now REFUSED (PYCSL-R486-NONSCALAR-AUGASSIGN-TARGET).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model store
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(t: Tuple[List[int], int]) -> int:
    t[0] *= 2
    return 0


if __name__ == "__main__":
    try:
        r = f(([0], 1))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
