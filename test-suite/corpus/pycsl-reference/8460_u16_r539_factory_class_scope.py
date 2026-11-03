r"""Test 8460 -- route #539 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1106/bg1000_lam_class_scope_name.py): a `default_factory` lambda reading a class-body name in a constructor judged by route #519; CPython NameError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses
@dataclasses.dataclass
class P:
    K = 5
    a: int
    b: Any = dataclasses.field(default_factory=lambda: K)


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
