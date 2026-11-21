r"""Test 8707 -- route #550 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 52 probe g1313/bn1223_e_iter_list_post.py): `list(It())` in a dataclass `__post_init__`, `__iter__` returning 5; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class It:
    def __iter__(self):
        return 5


@dataclass
class C:
    n: int

    def __post_init__(self) -> None:
        self.xs = list(It())


#@ no_exception \all
def f(k: int) -> int:
    c = C(k)
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
