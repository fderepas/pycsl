r"""Test 8599 -- route #542 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R542-NON-CONTAINER-OPERAND; red team 51 probe g1242/au1219_for_arith_result.py): `for c in k + 1`; CPython f(1) -> TypeError 'int' object is not iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int) -> int:
    c2 = 0
    for c in k * 2:
        c2 += 1
    return c2


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
