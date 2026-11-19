r"""Test 8541 -- route #540 (expected FAIL: PROVED at base, REFUSED PYCSL-R540-UNARY-PLUS-OPERAND; red team 51 probe pp1216_return_direct): `return +s` from a `-> str` def; CPython f("a") raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(s: str) -> str:
    return +s


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
