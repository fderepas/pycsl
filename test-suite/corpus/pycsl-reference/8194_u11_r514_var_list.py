r"""Test 8194 -- route #514 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R507-OVERFLOW-SITE-UNLOWERED; red team 47 probe g816/t8004_var_list): `r = range(n); list(r)`; CPython f(10**20) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    r = range(n)
    v = list(r)
    return 1


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
