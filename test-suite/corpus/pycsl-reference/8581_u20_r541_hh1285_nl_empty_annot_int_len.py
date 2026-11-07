r"""Test 8581 -- route #541 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R541-ELEMENT-KIND; red team 51 probe g1206/hh1285_nl_empty_annot_int_len.py): a `List[str]` local takes `.append(<int>)`; `len(p)` of the element; CPython f("ab", 3) -> TypeError object of type 'int' has no len()
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(s: str, k: int) -> int:
    a: List[str] = []
    a.append(k)
    n = 0
    for p in a:
        n += len(p)
    return n


if __name__ == "__main__":
    try:
        r = f("ab", 3)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
