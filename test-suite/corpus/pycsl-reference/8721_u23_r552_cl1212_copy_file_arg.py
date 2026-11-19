r"""Test 8721 -- route #552 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R552-VALUE-KIND-MISMATCH; red team 52 probe g1337/cl1212_copy_file_arg.py): `h(xs.copy())` into `def h(x: int)`; CPython TypeError
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
def f(k: int, xs: List[int], d: Dict[str, int], s: str) -> int:
    return h(xs.copy())


if __name__ == "__main__":
    try:
        r = f(1, [1], {"a": 1}, "a b")
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
