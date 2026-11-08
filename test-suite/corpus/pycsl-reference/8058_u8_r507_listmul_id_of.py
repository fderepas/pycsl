r"""Test 8058 -- route #507 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R507-OVERFLOW-SITE-UNLOWERED; red team 46 probe y7034_listmul_id_of): `id([0] * n)` lowers the argument opaquely, dropping route #414's bound; CPython f(10**20) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    v = id([0] * n)
    return 1


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
