r"""Test 8509 -- route #533 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1108/bi1015_cls_dc_initvar_req.py): a dataclass with a required InitVar as the factory; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses

@dataclasses.dataclass
class Q:
    m: dataclasses.InitVar[int]

    def __post_init__(self, m: int) -> None:
        self.k = m


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
