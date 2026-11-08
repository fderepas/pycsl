r"""Test 8543 -- route #540 (expected FAIL: PROVED at base, REFUSED PYCSL-R540-UNARY-PLUS-OPERAND; red team 51 probe ii1213_stmt_list_param): `+xs` of a `List[int]` parameter; CPython f([1]) raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(xs: List[int]) -> int:
    +xs
    return 1


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
