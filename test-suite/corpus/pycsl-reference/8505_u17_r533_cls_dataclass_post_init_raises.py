r"""Test 8505 -- route #533 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1102/bc1107_cls_dataclass_post_init_raises.py): a dataclass whose `__post_init__` raises as the factory
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses
@dataclasses.dataclass
class Q:
    k: int = 0

    def __post_init__(self) -> None:
        raise ValueError("q")


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
