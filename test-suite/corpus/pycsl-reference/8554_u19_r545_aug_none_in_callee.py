r"""Test 8554 -- route #545 (expected FAIL: PROVED at base, REFUSED PYCSL-R545-NONE-OPERAND; red team 51 probe am1215_in_callee): `n += None` in a callee `g()` reached by the claimed `f`; CPython f(1) raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def nothing() -> None:
    return None


#@ no_exception \all
def opt(k: int) -> Optional[int]:
    if k == 1:
        return None
    return k



def g() -> int:
    n = 0
    n += None
    return n


#@ no_exception \all
def f(k: int) -> int:
    return g()


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
