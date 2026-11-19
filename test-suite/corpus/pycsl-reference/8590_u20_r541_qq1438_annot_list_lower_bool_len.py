r"""Test 8590 -- route #541 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R541-ELEMENT-KIND; red team 51 probe g1213/qq1438_annot_list_lower_bool_len.py): a `list[str]` local takes `True`; `len(p)` of the element; CPython f(3) -> TypeError object of type 'bool' has no len()
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int) -> int:
    a: list[str] = []
    a.append(True)
    n = 0
    for p in a:
        n += len(p)
    return n


if __name__ == "__main__":
    try:
        r = f(3)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
