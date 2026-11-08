r"""Test 8744 -- route #557 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R557-SET-SUBSCRIPT; red team 53 probe g1417/dr1223_set_str_store.py): `ws["a"] = "b"` on a `Set[str]` parameter; CPython TypeError: 'set' object does not support item assignment
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

from typing import NamedTuple, Iterable, Mapping


class NT(NamedTuple):
    a: int
    b: int



#@ no_exception \all
def f(x: Set[str]) -> int:
    x[0] = "b"
    return 1


if __name__ == "__main__":
    try:
        r = f({"a"})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
