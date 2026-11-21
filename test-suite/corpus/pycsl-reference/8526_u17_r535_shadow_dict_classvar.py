r"""Test 8526 -- route #535 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1108/bi1090_shadow_dict_classvar.py): a class-body ClassVar `dict` used as the factory; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses
from typing import ClassVar


@dataclasses.dataclass
class P:
    dict: ClassVar[int] = 0
    a: int
    b: Any = dataclasses.field(default_factory=dict)


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
