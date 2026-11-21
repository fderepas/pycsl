r"""Test 8054 -- route #507 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R507-OVERFLOW-SITE-UNLOWERED; red team 46 probe t7115_strmul_param_sortedtup): `sorted((s * n, s * n))` of a str parameter drops route #414's bound; CPython f('ab', 10**20) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(s: str, n: int) -> int:
    zs: List[int] = []
    v = sorted((s * n, s * n))
    return 1


if __name__ == "__main__":
    try:
        r = f('ab', 10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
