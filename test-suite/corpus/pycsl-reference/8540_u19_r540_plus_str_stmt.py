r"""Test 8540 -- route #540 (expected FAIL: PROVED at base, REFUSED PYCSL-R540-UNARY-PLUS-OPERAND; red team 51 probe ii1209_stmt_str_param): `+s` as a statement, `s: str`; CPython f("a") raises TypeError (bad operand type for unary +)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(s: str) -> int:
    +s
    return 1


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
