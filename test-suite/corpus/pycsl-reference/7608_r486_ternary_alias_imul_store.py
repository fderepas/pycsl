r"""Test 7608 -- route #486 (expected FAIL): red-team 40 probe g98_y9804_ternary_alias_imul under `--memory-model store` -- `b = a if .. else a; b *= 2` (CPython extends `a` in place) PROVED at base 0c61bfc3f; now REFUSED (PYCSL-R486-NONSCALAR-AUGASSIGN-TARGET).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model store
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ requires len(a) == 2
#@ ensures \result == 2
#@ assigns \nothing
def f(a: List[int], n: int) -> int:
    b = a if n > 0 else a
    b *= 2
    return len(a)


if __name__ == "__main__":
    try:
        r = f([0, 0], 1)
        if not (r == 2):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
