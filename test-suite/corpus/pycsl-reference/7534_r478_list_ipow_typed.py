r"""Test 7534 -- route #478 (expected FAIL): red-team 39 probe g52_x2007_list_ipow under `--memory-model typed` -- `a **= 2` on a list parameter (CPython TypeError) PROVED at base d6abee90b (the augmented assignment lowered to integer arithmetic on the heap location); now REFUSED (PYCSL-R478-COLLECTION-PARAM-AUGASSIGN).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
#@ assigns \nothing
def f(a: List[int]) -> int:
    a **= 2
    return 0


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
