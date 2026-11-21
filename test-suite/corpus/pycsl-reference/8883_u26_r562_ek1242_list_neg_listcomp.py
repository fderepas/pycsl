r"""Test 8883 -- route #562 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R562-COMPREHENSION-ELEMENT-KIND; red team 53 probe g1436/ek1242_list_neg_listcomp.py): `return len([-xs for x in xs])`; CPython TypeError: bad operand type for unary -: 'list'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, xs: List[int], t: str, d: Dict[str, int], o: Optional[int] = None) -> int:
    return len([-xs for x in xs])


if __name__ == "__main__":
    try:
        r = f(1, [1, 2], "ab", {"a": 1})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
