r"""Test 7607 -- route #486 (expected FAIL): red-team 40 probe g85_m8923_walrus_alias_imul under `--memory-model typed` -- `(b := a); b *= 2; return len(a)` with `ensures \result == 2` (CPython 4) PROVED at base 0c61bfc3f; now REFUSED (PYCSL-R486-NONSCALAR-AUGASSIGN-TARGET).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ requires len(a) == 2
#@ ensures \result == 2
#@ assigns \nothing
def f(a: List[int]) -> int:
    (b := a)
    b *= 2
    return len(a)


if __name__ == "__main__":
    try:
        r = f([0, 0])
        if not (r == 2):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
