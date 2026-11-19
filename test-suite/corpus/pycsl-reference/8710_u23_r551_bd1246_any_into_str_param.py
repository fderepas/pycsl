r"""Test 8710 -- route #551 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R551-CONSTRUCTOR-ARGUMENT-KIND; red team 52 probe g1303/bd1246_any_into_str_param.py): an `Any` local bound to an int passed to a constructor parameter `s: str` whose body takes `len(s)`; CPython f(1) -> TypeError: object of type 'int' has no len()
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, s: str) -> None:
        self.n = len(s)


#@ no_exception \all
def f(k: int) -> int:
    v: Any = k
    c = C(v)
    return c.n


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
