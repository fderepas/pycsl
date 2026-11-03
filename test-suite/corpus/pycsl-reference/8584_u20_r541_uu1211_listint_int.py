r"""Test 8584 -- route #541 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R541-ELEMENT-KIND; red team 51 probe g1217/uu1211_listint_int.py): a `List[List[int]]` local takes `.append(k)`; `len(p)` of the element; CPython f(3) -> TypeError object of type 'int' has no len()
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int



#@ no_exception \all
def f(k: int) -> int:
    a: List[List[int]] = []
    a.append(k)
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
