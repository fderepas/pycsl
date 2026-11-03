r"""Test 8583 -- route #541 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R541-ELEMENT-KIND; red team 51 probe g1213/qq1305_annot_empty_int_upper.py): an empty `List[str]` local takes an int; `p.upper()` of the element; CPython f(3) -> AttributeError 'int' object has no attribute 'upper'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int) -> int:
    a: List[str] = []
    a.append(k)
    n = 0
    for p in a:
        n += len(p.upper())
    return n


if __name__ == "__main__":
    try:
        r = f(3)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
