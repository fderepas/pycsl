r"""Test 8549 -- route #545 (expected FAIL: PROVED at base, REFUSED PYCSL-R545-NONE-OPERAND; red team 51 probe ae1200_neg_nothing_ret): `return -nothing()` of a `-> None` def; CPython f(0) raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def nothing() -> None:
    return None


#@ no_exception \all
def opt(k: int) -> Optional[int]:
    if k == 0:
        return None
    return k


class C:
    #@ no_exception \all
    def m(self) -> None:
        return None



#@ no_exception \all
def f(k: int) -> int:
    return -nothing()


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
