r"""Test 8585 -- route #541 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R541-ELEMENT-KIND; red team 51 probe g1217/uu1214_rec_int.py): a `List[P]` local takes an int; the field read of the element; CPython f(3) -> AttributeError 'int' object has no attribute 'a'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int



#@ no_exception \all
def f(k: int) -> int:
    a: List[P] = []
    a.append(k)
    n = 0
    for p in a:
        n += p.a
    return n


if __name__ == "__main__":
    try:
        r = f(3)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
