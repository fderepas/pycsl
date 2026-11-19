r"""Test 8197 -- route #515 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R515-IMMEDIATELY-INVOKED-LAMBDA; red team 47 probe g818/v8033_tupmul_plain): `(lambda m: (1,) * m)(n)`; CPython f(10**20, "ab") raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int, s: str) -> int:
    w = (lambda m: (1,) * m)(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(10**20, "ab")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
