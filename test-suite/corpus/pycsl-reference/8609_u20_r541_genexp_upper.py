r"""Test 8609 -- route #541 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R541-ELEMENT-KIND; executor u20 probe beyond the red-team family): a `List[str]` local takes an int, read by a generator `sum(len(p.upper()) for p in a)`; CPython f(3) -> AttributeError 'int' object has no attribute 'upper'
"""
# pycsl-expected: FAIL
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class P:
    a: int


class Box:
    def __init__(self) -> None:
        self.items: List[str] = []


#@ no_exception \all
def f(k: int) -> int:
    a: List[str] = []
    a.append(k)
    return sum(len(p.upper()) for p in a)


if __name__ == "__main__":
    try:
        print(f(3))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
