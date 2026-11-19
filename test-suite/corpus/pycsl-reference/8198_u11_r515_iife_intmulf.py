r"""Test 8198 -- route #515 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R515-IMMEDIATELY-INVOKED-LAMBDA; red team 47 probe g818/v8065_intmulf_plain): `(lambda m: m * 0.5)(n)`; CPython f(10**400, "ab") raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int, s: str) -> int:
    w = (lambda m: m * 0.5)(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(10**400, "ab")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
