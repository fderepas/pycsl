r"""Test 8589 -- route #541 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R543-ANNOTATED-BINDING-KIND (the annotated display binding); red team 51 probe g1227/af1224_annot_list_int_lit_idx_len.py): a `List[str]` local initialised with an int display element; `len(a[0])`; CPython f(0) -> TypeError object of type 'int' has no len()
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def nothing() -> None:
    return None



#@ no_exception \all
def f(k: int) -> int:
    xs: List[str] = [1, 2]
    return len(xs[0])


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
