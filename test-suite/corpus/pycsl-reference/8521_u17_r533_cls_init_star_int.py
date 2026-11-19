r"""Test 8521 -- route #533 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1108/bi1011_cls_init_star_int.py): a factory class whose `__init__` stores `[*5]`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses

class Q:
    def __init__(self) -> None:
        self.k = [*5]


@dataclasses.dataclass
class P:
    a: int
    b: Any = dataclasses.field(default_factory=Q)


#@ no_exception \all
def f(n: int) -> int:
    p = P(n)
    return p.a


if __name__ == "__main__":
    try:
        r = f(5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
