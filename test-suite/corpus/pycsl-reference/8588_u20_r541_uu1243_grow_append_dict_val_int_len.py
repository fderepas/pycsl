r"""Test 8588 -- route #541 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R541-ELEMENT-KIND; red team 51 probe g1217/uu1243_grow_append_dict_val_int_len.py): a `List[str]` local takes an int dict value; `len(p)` of the element; CPython f(3) -> TypeError object of type 'int' has no len()
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int


def nothing() -> None:
    return None



#@ no_exception \all
def f(k: int) -> int:
    a: List[str] = []
    d = {"x": 1}
    a.append(d["x"])
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
