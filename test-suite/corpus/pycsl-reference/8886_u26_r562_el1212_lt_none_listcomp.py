r"""Test 8886 -- route #562 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R562-COMPREHENSION-ELEMENT-KIND; red team 53 probe g1437/el1212_lt_none_listcomp.py): `return len([x < None for x in xs])`; CPython TypeError: '<' not supported between instances of 'int' and 'NoneType'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int



#@ no_exception \all
def f(k: int, xs: List[int], t: str, d: Dict[str, int], p: P, s: Set[int]) -> int:
    return len([x < None for x in xs])


if __name__ == "__main__":
    try:
        r = f(1, [1, 2], "ab", {"a": 1}, P(1), {1})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
