r"""Test 7536 -- route #478 (expected FAIL): red-team 39 probe g52_x2002_list_iand under `--memory-model store` -- `a &= 1` on a list parameter (CPython TypeError) PROVED at base d6abee90b (the augmented assignment lowered to integer arithmetic on the heap location); now REFUSED (PYCSL-R478-COLLECTION-PARAM-AUGASSIGN).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model store
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
#@ assigns \nothing
def f(a: List[int]) -> int:
    a &= 1
    return 0


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
