r"""Test 8711 -- route #551 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R551-CONSTRUCTOR-ARGUMENT-KIND; red team 52 probe g1313/bn1260_f_any_call.py): the result of a `-> Any` function (an int) passed to `s: str`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, s: str) -> None:
        self.n = len(s)


def h(k: int) -> Any:
    return k


#@ no_exception \all
def f(k: int) -> int:
    c = C(h(k))
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
