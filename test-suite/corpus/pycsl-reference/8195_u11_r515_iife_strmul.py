r"""Test 8195 -- route #515 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R515-IMMEDIATELY-INVOKED-LAMBDA; red team 47 probe g818/v8001_strmul_plain): `(lambda m: "ab" * m)(n)`: the immediately-invoked lambda is erased to `(any int)`; CPython f(10**20, "ab") raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int, s: str) -> int:
    w = (lambda m: "ab" * m)(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(10**20, "ab")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
