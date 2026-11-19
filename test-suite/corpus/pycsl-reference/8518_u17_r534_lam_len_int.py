r"""Test 8518 -- route #534 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1102/bc1136_lam_len_int.py): `default_factory=lambda: len(5)`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses


@dataclasses.dataclass
class P:
    a: int
    b: Any = dataclasses.field(default_factory=lambda: len(5))


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
