r"""Test 8461 -- route #539 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1106/bg1002_lam_global_rebound_later.py): a `default_factory` lambda reading a global rebound after the class in a constructor judged by route #519; CPython TypeError: can only concatenate str
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses
K = 1


@dataclasses.dataclass
class P:
    a: int
    b: Any = dataclasses.field(default_factory=lambda: K + 1)


K = "a"


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
