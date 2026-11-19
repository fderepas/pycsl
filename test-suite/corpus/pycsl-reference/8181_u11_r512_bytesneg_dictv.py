r"""Test 8181 -- route #512 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R507-OVERFLOW-SITE-UNLOWERED; red team 47 probe g810/m8042_bytesneg_dictv): `{"k": bytes(n)}` at n = -1: the negative-count ValueError is dropped with the erased call; CPython f(-1) raises ValueError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    v = {"k": bytes(n)}
    return 1


if __name__ == "__main__":
    try:
        r = f(-1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
