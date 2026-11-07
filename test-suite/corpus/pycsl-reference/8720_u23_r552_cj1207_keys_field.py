r"""Test 8720 -- route #552 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R551-CONSTRUCTOR-ARGUMENT-KIND; red team 52 probe g1335/cj1207_keys_field.py): `R(d.keys())` for a dataclass field `a: int`, then `r.a + 1`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass



def h(x: int) -> int:
    return x + 1


@dataclass
class R:
    a: int


#@ no_exception \all
def f(k: int, xs: List[int], d: Dict[str, int]) -> int:
    r = R(d.keys())
    return r.a + 1


if __name__ == "__main__":
    try:
        r = f(1, [1], {"a": 1})
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
