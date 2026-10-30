r"""Test 7532 -- route #478 (expected FAIL): red-team 39 probe g45_m1200_list_imul2 under `--memory-model typed` -- `a *= 2; return len(a)` proved `\result == 2` (CPython 4) PROVED at base d6abee90b (the augmented assignment lowered to integer arithmetic on the heap location); now REFUSED (PYCSL-R478-COLLECTION-PARAM-AUGASSIGN).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ requires len(a) == 2
#@ ensures \result == 2
#@ assigns \nothing
def f(a: List[int]) -> int:
    a *= 2
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
