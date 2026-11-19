r"""Test 8714 -- route #551 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R551-CONSTRUCTOR-ARGUMENT-KIND; red team 52 probe g1313/bn1264_f_any_local_none.py): an `Any` local bound to None passed to `s: str`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, s: str) -> None:
        self.n = len(s)


#@ no_exception \all
def f(k: int) -> int:
    v: Any = None
    c = C(v)
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
