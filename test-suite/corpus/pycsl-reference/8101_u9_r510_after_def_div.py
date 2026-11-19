r"""Test 8101 -- route #510 (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 47 probe o8001_after_div): `n // K` under `no_exception \all` with K rebound by a later `type K = int`; CPython f(10) raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

K = 5


#@ no_exception \all
def f(n: int) -> int:
    return n // K

type K = int


if __name__ == "__main__":
    try:
        r = f(10)
        if r != 2:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
