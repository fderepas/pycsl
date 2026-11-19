r"""Test 8594 -- route #542 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R542-NON-CONTAINER-OPERAND; red team 51 probe g1228/ag1203_callee_in_none.py): an unclaimed callee does `"a" in None`; CPython f(1) -> TypeError argument of type 'NoneType' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(n: int) -> int:
    k = 0
    k = 1 if "a" in None else 0
    return k


#@ no_exception \all
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
