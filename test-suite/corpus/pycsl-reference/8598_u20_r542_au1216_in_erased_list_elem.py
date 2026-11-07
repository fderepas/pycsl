r"""Test 8598 -- route #542 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R541-ELEMENT-KIND (the store, before the read); red team 51 probe g1242/au1216_in_erased_list_elem.py): `"x" in a[0]` of an int stored into a `List[str]`; CPython f(1) -> TypeError argument of type 'int' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int) -> int:
    a: List[str] = []
    a.append(5)
    return 1 if "x" in a[0] else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
