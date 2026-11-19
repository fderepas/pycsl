r"""Test 8525 -- route #535 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1108/bi1088_shadow_complex_cls.py): a nested class-body `class complex` used as the factory; CPython raises
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses


@dataclasses.dataclass
class P:
    class complex:
        def __init__(self) -> None:
            raise ValueError("c")
    a: int
    b: Any = dataclasses.field(default_factory=complex)


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
