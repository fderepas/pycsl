r"""Test 8184 -- route #512 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 47 probe g813/q8003_bytes_req_field): `self.data = bytes(n)` in a constructor under `requires n >= 0`: the field initialiser is erased (route #315 counted `bytes` as total); CPython f(10**20) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class Buf:
    def __init__(self, n: int) -> None:
        self.data = bytes(n)


#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    k = Buf(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
