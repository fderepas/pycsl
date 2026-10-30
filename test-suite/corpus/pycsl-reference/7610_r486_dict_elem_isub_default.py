r"""Test 7610 -- route #486 (expected FAIL): red-team 40 probe g107_e10703_dict_elem_isub -- in the DEFAULT model: `a[0] -= 1` on `a: List[Dict[int, int]]` (CPython TypeError) was NOT-PROVED at base 0c61bfc3f (Why3 typing, fail closed); the repair's type judgement now REFUSES it under every memory model (PYCSL-R486-NONSCALAR-AUGASSIGN-TARGET).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ requires len(a) == 1
#@ no_exception \all
def f(a: List[Dict[int, int]]) -> int:
    a[0] -= 1
    return 0


if __name__ == "__main__":
    try:
        r = f([{}])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
